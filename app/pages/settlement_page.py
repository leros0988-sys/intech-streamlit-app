import streamlit as st
import pandas as pd

from app.settlement.uploader import upload_multiple_files
from app.settlement.classifier import classify_uploaded_files
from app.settlement.processor import process_file
from app.settlement.missing import (
    extract_settle_ids_from_multi,
    extract_settle_ids_from_kakao,
    find_missing_settle_ids,
)
from app.settlement.summary import (
    calculate_revenue,
    create_draft_table,
    top3_revenue,
    revenue_by_region,
)
from app.settlement.pdf_generator import (
    generate_pdfs_from_df,
    make_zip,
)
from app.settlement.utils import (
    df_to_excel_bytes,
    format_money,
    safe_filename,
    clean_df,
)


# -------------------------------------------------------
# 세션 초기화 헬퍼
# -------------------------------------------------------
def init_state():
    defaults = {
        "settlement_data_map": None,
        "settlement_classified": None,
        "settlement_all_processed": None,
        "settlement_multi_df": None,
        "settlement_missing_df": None,
        "settlement_revenue": None,
        "settlement_draft": None,
        "settlement_pdf_dict": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -------------------------------------------------------
# VAT 컬럼 자동 감지 (기안자료용 부가세 포함/미포함 대략 분류)
# -------------------------------------------------------
def detect_vat_column(df: pd.DataFrame):
    for c in df.columns:
        name = str(c)
        if "부가세" in name or "VAT" in name.upper():
            return c
    return None


def main():
    st.markdown(
        "<h2 style='margin-bottom:10px;'>📑 정산 페이지</h2>",
        unsafe_allow_html=True,
    )
    st.caption("대금청구서 + 카카오 통계를 기준으로 정산·누락기관·PDF·기안자료까지 한 번에 처리합니다.")

    init_state()

    st.write("")

    # ---------------------------------------------------
    # 1) 엑셀 업로드
    # ---------------------------------------------------
    with st.expander("1️⃣ 엑셀 업로드 (대금청구서 + 카카오 통계)", expanded=True):
        st.write("대금청구서 엑셀, 카카오 통계 엑셀 등을 한 번에 업로드하세요.")

        data_map = upload_multiple_files()
        if data_map:
            st.session_state["settlement_data_map"] = data_map
            st.success(f"총 {len(data_map)}개 파일을 읽었습니다.")
            st.write("업로드된 파일 목록:")
            st.table(
                pd.DataFrame(
                    [
                        {"파일명": name, "행 수": len(df)}
                        for name, df in data_map.items()
                    ]
                )
            )
        else:
            st.info("아직 업로드된 파일이 없거나 유효한 데이터가 없습니다.")

    # ---------------------------------------------------
    # 2) 검증하기 (회사 분류 + 표준화)
    # ---------------------------------------------------
    with st.expander("2️⃣ 검증하기 (파일 구조 / 회사 자동 분류)", expanded=False):
        if st.session_state["settlement_data_map"] is None:
            st.warning("먼저 엑셀 파일을 업로드해주세요.")
        else:
            if st.button("🔍 검증 실행", key="btn_validate"):
                data_map = st.session_state["settlement_data_map"]

                # 2-1. 회사 분류
                classified = classify_uploaded_files(data_map)
                st.session_state["settlement_classified"] = classified

                st.subheader("📂 파일 분류 결과")
                info_rows = []
                for item in classified:
                    info_rows.append(
                        {
                            "파일명": item["filename"],
                            "판별 회사": item["company"],
                            "행 수": len(item["df"]),
                        }
                    )
                st.table(pd.DataFrame(info_rows))

                # 2-2. 회사별 정산 처리 (kakao/kt/naver)
                processed_list = []
                multi_df = None

                for item in classified:
                    company = item["company"]
                    df = item["df"]

                    if company in ["kakao", "kt", "naver"]:
                        proc = process_file(df, company)
                        processed_list.append(proc)
                    elif company == "multi":
                        # 대금청구서(다수기관) 파일로 간주
                        multi_df = clean_df(df)

                if processed_list:
                    all_processed = pd.concat(processed_list, ignore_index=True)
                    st.session_state["settlement_all_processed"] = all_processed

                    st.subheader("📊 정산용 표준 데이터(미리보기)")
                    st.dataframe(all_processed.head(50))
                else:
                    st.warning("정산 처리 가능한 카카오/KT/네이버 파일이 없습니다.")

                if multi_df is not None:
                    st.session_state["settlement_multi_df"] = multi_df
                    st.success("다수기관 대금청구서 파일도 인식했습니다.")
                    st.dataframe(multi_df.head(20))
                else:
                    st.info("대금청구서(다수기관) 파일은 발견되지 않았습니다. 'multi' 패턴 파일이 필요합니다.")

    # ---------------------------------------------------
    # 3) 누락 기관 체크 (SettleID 기준)
    # ---------------------------------------------------
    with st.expander("3️⃣ 누락 기관 체크 (Settle ID 기준)", expanded=False):
        multi_df = st.session_state["settlement_multi_df"]
        classified = st.session_state["settlement_classified"]

        if multi_df is None or classified is None:
            st.warning("검증 단계를 먼저 실행해주세요.")
        else:
            if st.button("⚠ 누락 체크 실행", key="btn_missing"):
                try:
                    base_ids = extract_settle_ids_from_multi(multi_df)

                    # 카카오 파일들만 모아서 합치기
                    kakao_list = [
                        item["df"] for item in classified if item["company"] == "kakao"
                    ]
                    if not kakao_list:
                        st.warning("카카오 통계 파일이 없어 누락 체크를 할 수 없습니다.")
                    else:
                        kakao_ids_list = [
                            extract_settle_ids_from_kakao(df) for df in kakao_list
                        ]
                        kakao_ids = pd.concat(kakao_ids_list, ignore_index=True)
                        kakao_ids = kakao_ids.drop_duplicates(subset=["기관명"])

                        missing_df = find_missing_settle_ids(base_ids, kakao_ids)
                        st.session_state["settlement_missing_df"] = missing_df

                        if missing_df.empty:
                            st.success("Settle ID 기준 누락 기관이 없습니다. (완벽!)")
                        else:
                            st.error(f"총 {len(missing_df)}개 기관이 누락되었습니다.")
                            st.dataframe(missing_df)

                            st.download_button(
                                "📥 누락 기관 리스트 엑셀 다운로드",
                                data=df_to_excel_bytes(missing_df),
                                file_name="누락기관_리스트.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                except Exception as e:
                    st.error(f"누락 체크 중 오류: {e}")

    # ---------------------------------------------------
    # 4) 통계 보기 (총매출 / 회사별 / TOP3 / 지역별)
    # ---------------------------------------------------
    with st.expander("4️⃣ 통계 보기 (총매출 / 회사별 / TOP3 / 지역별)", expanded=False):
        all_processed = st.session_state["settlement_all_processed"]

        if all_processed is None:
            st.warning("검증에서 정산 데이터가 만들어지지 않았습니다.")
        else:
            if st.button("📊 통계 계산", key="btn_stats"):
                try:
                    # 총매출 + 회사별 매출
                    revenue = calculate_revenue(all_processed)
                    st.session_state["settlement_revenue"] = revenue

                    total_rev = revenue["total_revenue"]
                    st.markdown(
                        f"### 💰 이번 달 총 매출 : **{format_money(total_rev)} 원**"
                    )

                    # 회사별 매출
                    comp_map = revenue["company_revenue"]
                    comp_df = pd.DataFrame(
                        [
                            {
                                "정산회사": k,
                                "매출": v,
                                "매출(포맷)": format_money(v),
                            }
                            for k, v in comp_map.items()
                        ]
                    )
                    st.markdown("#### 🏢 회사별 매출")
                    st.table(comp_df)

                    # 기안자료용 상세 테이블
                    draft = create_draft_table(all_processed)
                    st.session_state["settlement_draft"] = draft

                    # TOP3
                    st.markdown("#### 🏆 기관별 매출 TOP3")
                    top3 = draft["top3"]
                    if not top3.empty:
                        top3["매출(포맷)"] = top3["매출"].apply(format_money)
                        st.table(top3)
                    else:
                        st.info("기관명 기준 집계가 불가능합니다.")

                    # 지역별
                    st.markdown("#### 🗺 지역별 매출")
                    region_df = draft["region_sum"]
                    if not region_df.empty:
                        region_df["매출(포맷)"] = region_df["매출"].apply(format_money)
                        st.table(region_df)
                    else:
                        st.info("지역별 매출 집계가 없습니다.")

                except Exception as e:
                    st.error(f"통계 계산 중 오류: {e}")

    # ---------------------------------------------------
    # 5) PDF 생성 (기관별 PDF + ZIP)
    # ---------------------------------------------------
    with st.expander("5️⃣ PDF 생성 (기관별 PDF + ZIP)", expanded=False):
        multi_df = st.session_state["settlement_multi_df"]

        if multi_df is None:
            st.warning("대금청구서(다수기관) 파일이 필요합니다. 검증 단계에서 인식되었는지 확인하세요.")
        else:
            if st.button("📄 기관별 PDF 생성", key="btn_pdf"):
                try:
                    pdf_dict = generate_pdfs_from_df(multi_df)
                    st.session_state["settlement_pdf_dict"] = pdf_dict

                    st.success(f"총 {len(pdf_dict)}개 기관에 대한 PDF를 생성했습니다.")

                    # 전체 ZIP
                    zip_bytes = make_zip(pdf_dict)
                    st.download_button(
                        "📦 전체 기관 PDF ZIP 다운로드",
                        data=zip_bytes,
                        file_name="정산_PDF_전체.zip",
                        mime="application/zip",
                    )

                    # 선택 ZIP
                    st.markdown("---")
                    st.markdown("#### ✅ 선택한 기관만 ZIP으로 받기")
                    filenames = sorted(pdf_dict.keys())
                    selected = st.multiselect(
                        "ZIP으로 묶고 싶은 기관 PDF를 선택하세요.",
                        options=filenames,
                    )
                    if selected:
                        sub_dict = {k: pdf_dict[k] for k in selected}
                        sub_zip = make_zip(sub_dict)
                        st.download_button(
                            "📦 선택한 기관만 ZIP 다운로드",
                            data=sub_zip,
                            file_name="정산_PDF_선택.zip",
                            mime="application/zip",
                        )

                except Exception as e:
                    st.error(f"PDF 생성 중 오류: {e}")

    # ---------------------------------------------------
    # 6) 기안자료 생성
    # ---------------------------------------------------
    with st.expander("6️⃣ 기안자료 생성 (요약 문안 자동 생성)", expanded=False):
        draft = st.session_state["settlement_draft"]
        revenue = st.session_state["settlement_revenue"]
        multi_df = st.session_state["settlement_multi_df"]
        missing_df = st.session_state["settlement_missing_df"]

        if draft is None or revenue is None or multi_df is None:
            st.warning("통계 계산과 검증 단계를 먼저 완료해주세요.")
        else:
            if st.button("📝 기안자료 문안 생성", key="btn_draft"):
                try:
                    total_rev = revenue["total_revenue"]
                    comp_map = revenue["company_revenue"]
                    comp_name_map = {
                        "kakao": "카카오",
                        "kt": "KT",
                        "naver": "네이버",
                    }

                    # 기관 수
                    try:
                        org_count = multi_df["기관명"].astype(str).str.strip().nunique()
                    except Exception:
                        org_count = len(multi_df)

                    # 누락 기관 수
                    missing_count = (
                        0
                        if (missing_df is None or missing_df.empty)
                        else len(missing_df)
                    )

                    # 부가세 포함/미포함 대략 집계
                    vat_text = ""
                    vat_col = detect_vat_column(multi_df)
                    if vat_col:
                        amount_col = (
                            "청구금액"
                            if "청구금액" in multi_df.columns
                            else "총금액" if "총금액" in multi_df.columns else None
                        )
                        if amount_col:
                            vat_group = (
                                multi_df.groupby(vat_col)[amount_col]
                                .sum()
                                .reset_index()
                            )
                            lines = []
                            for _, r in vat_group.iterrows():
                                label = str(r[vat_col])
                                val = format_money(r[amount_col])
                                lines.append(f"    - {label}: {val}원")
                            if lines:
                                vat_text = (
                                    "4. 부가세 포함 여부별 청구금액\n" + "\n".join(lines) + "\n"
                                )

                    # 회사별 매출 텍스트
                    comp_lines = []
                    for k, v in comp_map.items():
                        nm = comp_name_map.get(k, k)
                        comp_lines.append(f"    - {nm}: {format_money(v)}원")

                    # TOP3
                    top3_df = draft["top3"]
                    top3_lines = []
                    if top3_df is not None and not top3_df.empty:
                        for _, r in top3_df.iterrows():
                            org = r["기관명"]
                            amt = format_money(r["매출"])
                            top3_lines.append(f"    - {org}: {amt}원")

                    # 지역별
                    region_df = draft["region_sum"]
                    region_lines = []
                    if region_df is not None and not region_df.empty:
                        for _, r in region_df.iterrows():
                            region = r["지역"]
                            amt = format_money(r["매출"])
                            region_lines.append(f"    - {region}: {amt}원")

                    # 실제 문안
                    text_lines = []

                    text_lines.append("1. 정산 개요")
                    text_lines.append(
                        f"    - 이번 달 정산 대상 기관은 총 {org_count}개 기관입니다."
                    )
                    text_lines.append(
                        f"    - 이번 달 총 매출액은 {format_money(total_rev)}원입니다."
                    )
                    text_lines.append(
                        f"    - 이 중 정산 누락(Settle ID 미등록) 의심 기관은 {missing_count}개 기관입니다."
                    )
                    text_lines.append("")

                    text_lines.append("2. 회사별 매출 현황")
                    if comp_lines:
                        text_lines.extend(comp_lines)
                    else:
                        text_lines.append("    - 회사별 매출 집계 불가")

                    text_lines.append("")
                    text_lines.append("3. 기관별 매출 상위 3개 기관")
                    if top3_lines:
                        text_lines.extend(top3_lines)
                    else:
                        text_lines.append("    - 상위 3개 기관 집계 불가")

                    text_lines.append("")
                    if vat_text:
                        text_lines.append(vat_text.rstrip())
                        text_lines.append("")
                    else:
                        text_lines.append("4. 부가세 포함 여부별 집계")
                        text_lines.append("    - 부가세 관련 컬럼을 찾지 못해 집계하지 못했습니다.")
                        text_lines.append("")

                    text_lines.append("5. 지역별 매출 현황")
                    if region_lines:
                        text_lines.extend(region_lines)
                    else:
                        text_lines.append("    - 지역별 매출 집계 불가")

                    text = "\n".join(text_lines)

                    st.markdown("#### ✨ 생성된 기안자료 문안")
                    st.text_area("", value=text, height=300)

                    st.download_button(
                        "📥 기안자료 텍스트 다운로드",
                        data=text.encode("utf-8"),
                        file_name="정산_기안자료_요약.txt",
                        mime="text/plain",
                    )

                    if missing_count > 0 and missing_df is not None and not missing_df.empty:
                        st.markdown("---")
                        st.markdown("#### 🔎 참고: 누락 기관 리스트")
                        st.dataframe(missing_df)

                except Exception as e:
                    st.error(f"기안자료 생성 중 오류: {e}")


# ---------------------------------------------------
# 페이지 실행 함수 이름을 settlement_page 로 정의해야 함
# ---------------------------------------------------
def settlement_page():
    main()


if __name__ == "__main__":
    settlement_page()
