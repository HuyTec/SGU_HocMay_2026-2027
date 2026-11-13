from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def save_validation_plot(results, target, output_path, hours=168):
    if not results:
        raise ValueError("Không có kết quả để vẽ.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_rows = min(hours, len(target))
    times = target["date_time"].iloc[:n_rows]
    actual = target["traffic_volume"].iloc[:n_rows]

    fig, axes = plt.subplots(
        len(results),
        1,
        figsize=(14, 11),
        sharex=True,
        sharey=True,
        layout="constrained",
        squeeze=False,
    )

    for ax, item in zip(axes[:, 0], results):
        prediction = item["prediction"][:n_rows]

        ax.plot(
            times,
            actual,
            color="#202020",
            linewidth=1.5,
            label="Thực tế",
        )
        ax.plot(
            times,
            prediction,
            color="tab:orange",
            linestyle="--",
            linewidth=1.2,
            label="Dự đoán",
        )
        ax.set_title(item["model"], loc="left")
        ax.set_ylabel("Xe/giờ")
        ax.grid(alpha=0.25)
        ax.legend(loc="upper right")

    axes[-1, 0].xaxis.set_major_locator(
        mdates.HourLocator(byhour=[0, 12])
    )
    axes[-1, 0].xaxis.set_major_formatter(
        mdates.DateFormatter("%d/%m\n%H:%M")
    )
    axes[-1, 0].set_xlabel("Ngày và giờ")

    fig.suptitle("Config C — thực tế và dự đoán trên validation")
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)

    return output_path
