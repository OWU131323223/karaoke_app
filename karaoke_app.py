import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# ファイル名
CSV_FILE = "karaoke_data.csv"

# CSV読み込み or 初期化
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df["点数"] = pd.to_numeric(df["点数"], errors="coerce")  # 数値に変換
else:
    df = pd.DataFrame(columns=["題名", "ジャンル", "点数", "感想", "登録日"])

st.title("🎤 カラオケ十八番管理アプリ（完全版・AIなし）")

# ====== 曲登録フォーム ======
st.header("🎵 曲を登録する")
with st.form("form"):
    title = st.text_input("曲名")
    genre = st.selectbox("ジャンル", ["J-POP", "ロック", "アニソン", "演歌", "洋楽", "その他"])
    score = st.number_input("点数", min_value=0, max_value=100, step=1)
    memo = st.text_area("感想・メモ")
    submit = st.form_submit_button("保存する")

    if submit and title:
        date = datetime.now().strftime("%Y-%m-%d")
        new_data = pd.DataFrame([[title, genre, score, memo, date]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"「{title}」を保存しました！")

# ====== フィルター ======
st.header("📋 登録一覧とフィルター")
genres = ["すべて"] + sorted(df["ジャンル"].unique())
selected_genre = st.selectbox("ジャンルで絞り込み", genres)

# フィルタリング
if selected_genre != "すべて":
    filtered_df = df[df["ジャンル"] == selected_genre]
else:
    filtered_df = df

# ====== 編集・削除機能 ======
st.subheader("✏️ 曲の編集・削除")
if not df.empty:
    row_idx = st.number_input("編集または削除したい曲の番号（0〜）", min_value=0, max_value=len(df) - 1, step=1)
    selected_row = df.iloc[row_idx]

    with st.expander("選択中のデータを表示"):
        st.write(selected_row)

    if st.button("❌ この曲を削除する"):
        df = df.drop(df.index[row_idx]).reset_index(drop=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("削除しました！")

    with st.form("edit_form"):
        new_title = st.text_input("新しい曲名", value=selected_row["題名"])
        new_genre = st.selectbox("新しいジャンル", ["J-POP", "ロック", "アニソン", "演歌", "洋楽", "その他"], index=["J-POP", "ロック", "アニソン", "演歌", "洋楽", "その他"].index(selected_row["ジャンル"]))
        new_score = st.number_input("新しい点数", value=int(selected_row["点数"]), min_value=0, max_value=100)
        new_memo = st.text_area("新しいメモ", value=selected_row["感想"])
        if st.form_submit_button("更新する"):
            df.at[row_idx, "題名"] = new_title
            df.at[row_idx, "ジャンル"] = new_genre
            df.at[row_idx, "点数"] = new_score
            df.at[row_idx, "感想"] = new_memo
            df.to_csv(CSV_FILE, index=False)
            st.success("更新しました！")

# ====== 表示 ======
st.subheader("🎼 登録された曲一覧")
st.dataframe(filtered_df)
st.caption(f"登録曲数：{len(filtered_df)} 件")

# ====== 統計 ======
if not filtered_df.empty:
    st.subheader("📊 曲ごとの平均点・最高点")
    grouped = filtered_df.groupby("題名")["点数"]
    stats_df = pd.DataFrame({
        "平均点": grouped.mean().round(1),
        "最高点": grouped.max()
    }).sort_values(by="平均点", ascending=False)
    st.dataframe(stats_df)



# ====== 曲ごとの折れ線グラフ ======
    st.subheader("📈 曲ごとの点数推移グラフ")
    for song_title in filtered_df["題名"].unique():
        song_df = filtered_df[filtered_df["題名"] == song_title].sort_values(by="登録日")

        if len(song_df) < 2:
            continue  # 点数が1件しかない曲はスキップ

        st.markdown(f"**🎵 {song_title}**")
        fig3, ax3 = plt.subplots()
        ax3.plot(song_df["登録日"], song_df["点数"], marker="o")
        ax3.set_xlabel("登録日")
        ax3.set_ylabel("点数")
        ax3.set_title(f"{song_title} の点数推移")
        plt.xticks(rotation=45)
        st.pyplot(fig3)
