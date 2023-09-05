from glob import glob

import pandas as pd
from src import download_data, vis_data

if __name__ == "__main__":
    try:
        # ----- NOTE: [Data Download & Load] ----- #
        dd = download_data()
        dd.main()
        file_name = glob("*.xls")[0]
        data = pd.read_excel(file_name)

        # ----- NOTE: [전체 산업기능요원] ----- #
        vd = vis_data(file_name, data, 0)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("업종", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("현역 복무인원")
        vd.rank_vis("현역 편입인원")

        # ----- NOTE: [IT 산업기능요원] ----- #
        vd = vis_data(file_name, data, 1)
        vd.time_tsv()
        vd.pie_hist("지방청", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("현역 복무인원")
        vd.rank_vis("현역 편입인원")
        vd.rank_readme()
        vd.plot_time()

    except Exception as e:
        print(e)
        dd._send_discord_message(
            ":warning:" * 10
            + "ERROR!!!"
            + ":warning:" * 10
            + "\n"
            + "Awesome SGY\n"
            + "```\n"
            + str(e)
            + "\n```",
        )
