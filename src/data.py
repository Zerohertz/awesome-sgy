import os
import shutil
import warnings
from collections import defaultdict
from glob import glob

import pandas as pd
import seaborn as sns
import zerohertzLib as zz
from matplotlib import pyplot as plt

warnings.filterwarnings("ignore")


def _name(name):
    return (
        name.replace("(", "").replace(")", "").replace("/", "").replace(" ", "").lower()
    )


def _move(fr, to):
    path = os.path.join(to, os.path.basename(fr))
    if os.path.isfile(path):
        os.remove(path)
    shutil.move(fr, to)


class DataLoader:
    def __init__(self, file_name, degree):
        zz.plot.font(True, 12)
        self.time = file_name[-12:-4]
        self.data = pd.read_excel(file_name)
        """
        NOTE: "정보처리", "게임S/W"을 포함하는 산업기능요원을 IT 분야로 정의
        """
        os.makedirs("prop", exist_ok=True)
        DIR_NAME = ["ALL", "MS", "PhD"]
        DIR_NAME = ["ALL", "IT"]
        self.degree = DIR_NAME[degree]
        self.logger = zz.logging.Logger(f"SGY-{self.degree}")
        self.dir = os.path.join("prop", DIR_NAME[degree])
        os.makedirs(self.dir, exist_ok=True)
        if degree == 1:
            self.data = self.data[
                (self.data["업종"] == "정보처리") | (self.data["업종"] == "게임S/W")
            ]
        self.data["위치"] = (
            self.data["주소"]
            .str.replace("서울특별시 ", "서울특별시")
            .str.replace("경기도 ", "경기도")
            .str.split(" ")
            .str[0]
            .str.replace("서울특별시", "서울특별시 ")
            .str.replace("경기도", "경기도 ")
        )
        self.data["편입인원"] = (
            self.data["보충역 편입인원"] + self.data["현역 편입인원"]
        )
        self.data["복무인원"] = (
            self.data["보충역 복무인원"] + self.data["현역 복무인원"]
        )
        self.ranked_data_org = self.data.sort_values(
            by=["복무인원", "업체명"], ascending=[False, True]
        ).loc[
            :,
            [
                "업체명",
                "보충역 배정인원",
                "보충역 편입인원",
                "보충역 복무인원",
                "현역 배정인원",
                "현역 편입인원",
                "현역 복무인원",
                "편입인원",
                "복무인원",
            ],
        ]
        self.ranked_data_new = self.data.sort_values(
            by=["편입인원", "업체명"], ascending=[False, True]
        ).loc[
            :,
            [
                "업체명",
                "보충역 배정인원",
                "보충역 편입인원",
                "보충역 복무인원",
                "현역 배정인원",
                "현역 편입인원",
                "현역 복무인원",
                "편입인원",
                "복무인원",
            ],
        ]

    def time_tsv(self):
        self.logger.info("Time Series Data to TSV: START")
        for name, _, a, b, _, c, d, e, f in self.ranked_data_org.values:
            file_path = f"prop/time/data/{_name(name)}.tsv"
            with open(file_path, "a") as file:
                file.writelines(f"{self.time}\t{name}\t{a}\t{b}\t{c}\t{d}\t{e}\t{f}\n")
        self.logger.info("Time Series Data to TSV: DONE")

    def bar(self, tar):
        self.logger.info(f"Plot Bar Chart ({tar}): START")
        field_counts = self.data[tar].value_counts()
        zz.plot.figure((30, 10))
        colors = sns.color_palette("coolwarm", n_colors=len(field_counts))[::-1]
        zz.plot.barv(
            field_counts.to_dict(),
            xlab=tar,
            ylab="빈도",
            title="",
            colors=colors,
            rot=90,
            dim="%",
            save=False,
        )
        path = zz.plot.savefig(tar)
        _move(path, self.dir)
        self.logger.info(f"Plot Bar Chart ({tar}): DONE")

    def rank_vis(self, by="복무인원", top=30):
        self.logger.info(f"Plot Rank ({by}): START")
        plt.figure(figsize=(10, int(0.6 * top)))
        plt.grid(zorder=0)
        data = defaultdict(list)
        if by == "복무인원":
            for name, _, a, b, _, c, d, _, _ in self.ranked_data_org.iloc[:30].values[
                ::-1
            ]:
                data["yticks"].append(name)
                data["현역 복무인원"].append(d - c)
                data["현역 편입인원"].append(c)
                data["보충역 복무인원"].append(b - a)
                data["보충역 편입인원"].append(a)
            zz.plot.barh(
                data,
                title=f"{by} TOP {top}",
                colors=["#ff6060", "#f0c0c0", "#6060ff", "#c0c0f0"],
                dim="명",
                dimsize=10,
                sign=0,
                save=False,
            )
        elif by == "편입인원":
            for name, _, a, b, _, c, d, _, _ in self.ranked_data_new.iloc[:30].values[
                ::-1
            ]:
                data["yticks"].append(name)
                data["현역 편입인원"].append(c)
                data["보충역 편입인원"].append(a)
            zz.plot.barh(
                data,
                title=f"{by} TOP {top}",
                colors=["#ff6060", "#6060ff"],
                dim="명",
                dimsize=10,
                sign=0,
                save=False,
            )
        path = zz.plot.savefig(f"TOP_{top}_{by.replace(' ', '_')}")
        _move(path, self.dir)
        self.logger.info(f"Plot Rank ({by}): DONE")

    def rank_readme(self, top=0):
        self.logger.info("Write README.md: START")
        with open(f"{self.dir}/README.md", "w") as f:
            if top == 0:
                f.writelines(
                    "<div align=center> <h1> 🧑‍💻 산업기능요원 복무인원 순위 🧑‍💻 </h1> </div>\n\n<div align=center>\n\n|업체명|보충역 배정인원|보충역 편입인원|보충역 복무인원|현역 배정인원|현역 편입인원|현역 복무인원|총 편입인원|총 복무인원|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"
                )
                for name, a1, a2, a3, b1, b2, b3, t1, t2 in self.ranked_data_org.values:
                    f.writelines(
                        f"|[{name}](../time/plot/{_name(name)}.png)|{a1}|{a2}|{a3}|{b1}|{b2}|{b3}|{t1}|{t2}|\n"
                    )
            else:
                f.writelines(
                    f"<div align=center> <h1> 🧑‍💻 산업기능요원 복무인원 순위 TOP {top} 🧑‍💻 </h1> </div>\n\n<div align=center>\n\n|업체명|보충역 배정인원|보충역 편입인원|보충역 복무인원|현역 배정인원|현역 편입인원|현역 복무인원|총 편입인원|총 복무인원|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"
                )
                for name, a1, a2, a3, b1, b2, b3, t1, t2 in self.ranked_data_org[
                    :top
                ].values:
                    f.writelines(
                        f"|[{name}](../time/plot/{_name(name)}.png)|{a1}|{a2}|{a3}|{b1}|{b2}|{b3}|{t1}|{t2}|\n"
                    )
            f.writelines("\n</div>")
        self.logger.info("Write README.md: DONE")

    def plot_time(self, top=0):
        zz.util.rmtree("prop/time/plot")
        self.logger.info("Plot Time Series Data: START")
        # for path in glob("prop/time/data/*.tsv"):
        for _path in self.ranked_data_org.iloc[:top, 0]:
            path = f"prop/time/data/{_name(_path)}.tsv"
            self._plot_time(path)
        self.logger.info("Plot Time Series Data: DONE")

    def _plot_time(self, path):
        data = pd.read_csv(path, sep="\t", header=None, encoding="utf-8")
        name = data.iloc[:, 1][0]
        x, y1, y2, y3, y4, y5, y6 = (
            pd.to_datetime(data.iloc[:, 0], format="%Y%m%d"),
            data.iloc[:, 2],
            data.iloc[:, 3],
            data.iloc[:, 4],
            data.iloc[:, 5],
            data.iloc[:, 6],
            data.iloc[:, 7],
        )
        zz.plot.figure((20, 10))
        zz.plot.plot(
            x,
            {
                "보충역 편입인원": y1,
                "현역 편입인원": y3,
                "총 편입인원": y5,
                "보충역 복무인원": y2,
                "현역 복무인원": y4,
                "총 복무인원": y6,
            },
            xlab="Time",
            ylab="인원 [명]",
            title="",
            colors=["#c0c0f0", "#f0c0c0", "#909090", "#6060ff", "#ff6060", "#000000"],
            markersize=7,
            save=False,
        )
        try:
            m1 = self.data[self.data["업체명"] == name]["보충역 배정인원"].iloc[0]
            m2 = self.data[self.data["업체명"] == name]["현역 배정인원"].iloc[0]
            plt.title(f"{name}\n(보충역 배정인원: {m1}명, 현역 배정인원: {m2}명)")
        except:
            plt.title(f"{name}\n(배정인원: X)")
        path = zz.plot.savefig(_name(name), 100)
        _move(path, os.path.join("prop", "time", "plot"))


if __name__ == "__main__":
    paths = glob("data/*.xls")
    paths.sort()

    # zz.util.rmtree("prop/time/data")
    # for path in paths:
    #     dataloader = DataLoader(path, 0)
    #     dataloader.time_tsv()

    file_name = paths[-1]

    # ----- NOTE: [전체 산업기능요원] ----- #
    dataloader = DataLoader(file_name, 0)
    dataloader.bar("지방청")
    dataloader.bar("업종")
    dataloader.bar("위치")
    dataloader.rank_vis("복무인원")
    dataloader.rank_vis("편입인원")

    # ----- NOTE: [IT 산업기능요원] ----- #
    dataloader = DataLoader(file_name, 1)
    dataloader.time_tsv()
    dataloader.bar("지방청")
    dataloader.bar("위치")
    dataloader.rank_vis("복무인원")
    dataloader.rank_vis("편입인원")
    dataloader.rank_readme(1000)
    dataloader.plot_time(1000)
