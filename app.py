from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import os
import json


app = Flask(__name__)

load_dotenv()


# =========================
# OpenAI 配置
# =========================

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


# =========================
# 保存诊断记录
# =========================

def save_diagnosis(
    problem,
    summary,
    causes,
    steps,
    suggestions,
    mode
):

    conn = sqlite3.connect("diagnosis.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diagnosis_history
        (
            problem,
            summary,
            causes,
            steps,
            suggestions,
            mode
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        problem,
        summary,
        json.dumps(causes, ensure_ascii=False),
        json.dumps(steps, ensure_ascii=False),
        json.dumps(suggestions, ensure_ascii=False),
        mode
    ))

    conn.commit()
    conn.close()


# =========================
# 首页
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# 故障诊断
# =========================

@app.route("/diagnose", methods=["POST"])
def diagnose():

    data = request.get_json()

    problem = data.get("problem", "").strip()

    print("用户描述的问题：", problem)


    if not problem:

        return jsonify({
            "summary": "没有检测到问题描述。",
            "causes": [],
            "steps": [],
            "suggestions": [],
            "mode": "Demo"
        })


    # =========================
    # 尝试使用 AI
    # =========================

    try:

        if client is None:

            raise Exception(
                "未配置 OPENAI_API_KEY，使用 Demo 模式"
            )


        response = client.responses.create(

            model="gpt-5.6-luna",

            instructions="""
你是一个电脑故障诊断助手。

根据用户提供的电脑、Windows、软件或游戏故障描述，
进行初步分析。

请输出：

问题分析：
简要总结问题。

可能原因：
列出 2~4 个可能原因。

排查步骤：
按照优先级列出用户应该进行的检查。

建议解决方案：
给出对应的解决办法。

需要补充的信息：
列出进一步判断所需要的信息。

不要假装已经确定故障原因。
信息不足时，要明确说明这是初步判断。
""",

            input=problem
        )


        ai_answer = response.output_text


        save_diagnosis(
            problem,
            ai_answer,
            [],
            [],
            [],
            "AI"
        )


        return jsonify({

            "summary": ai_answer,

            "causes": [],

            "steps": [],

            "suggestions": [],

            "mode": "AI"

        })


    # =========================
    # AI 不可用 → Demo 模式
    # =========================

    except Exception as error:

        print("AI API 调用失败：", error)

        print("切换到本地 Demo 模式")


        causes = []

        steps = []

        suggestions = []


        # =========================
        # 闪退 / 崩溃
        # =========================

        if "闪退" in problem or "崩溃" in problem:

            causes.append(
                "软件或游戏可能存在兼容性问题"
            )

            causes.append(
                "运行库或系统组件可能存在异常"
            )

            steps.append(
                "确认问题是否每次启动都会出现"
            )

            steps.append(
                "检查软件或游戏是否支持当前 Windows 版本"
            )

            steps.append(
                "检查 Windows 事件查看器中的错误信息"
            )

            suggestions.append(
                "尝试以兼容模式运行"
            )

            suggestions.append(
                "检查并安装程序需要的运行库"
            )


        # =========================
        # 显卡 / 驱动
        # =========================

        if "显卡" in problem or "驱动" in problem:

            causes.append(
                "显卡驱动可能存在兼容性问题"
            )

            steps.append(
                "确认当前显卡型号和驱动版本"
            )

            steps.append(
                "检查问题是否发生在更新显卡驱动之后"
            )

            suggestions.append(
                "尝试更新到较新的稳定驱动"
            )

            suggestions.append(
                "如果问题出现在更新驱动之后，可以尝试回退驱动"
            )


        # =========================
        # 启动 / 打不开
        # =========================

        if "启动" in problem or "打不开" in problem:

            causes.append(
                "程序启动所需文件或运行环境可能存在问题"
            )

            steps.append(
                "确认程序文件是否完整"
            )

            steps.append(
                "查看是否存在错误提示"
            )

            steps.append(
                "尝试以管理员身份运行"
            )

            suggestions.append(
                "检查程序安装目录"
            )

            suggestions.append(
                "重新安装缺失的运行组件"
            )


        # =========================
        # 蓝屏
        # =========================

        if "蓝屏" in problem:

            causes.append(
                "Windows 驱动或硬件可能存在异常"
            )

            steps.append(
                "记录蓝屏错误代码"
            )

            steps.append(
                "检查最近是否更新过驱动"
            )

            steps.append(
                "检查 Windows 系统日志"
            )

            suggestions.append(
                "检查并更新相关驱动"
            )

            suggestions.append(
                "使用 Windows 系统工具检查系统文件"
            )


        # =========================
        # 网络
        # =========================

        if (
            "网络" in problem
            or "网速" in problem
            or "掉线" in problem
        ):

            causes.append(
                "网络连接或网络配置可能存在问题"
            )

            steps.append(
                "检查其他设备是否可以正常联网"
            )

            steps.append(
                "检查是否只有当前软件无法联网"
            )

            steps.append(
                "尝试重新连接网络"
            )

            suggestions.append(
                "重启路由器和电脑"
            )

            suggestions.append(
                "检查网络适配器状态"
            )


        # =========================
        # 卡顿 / 掉帧
        # =========================

        if "卡顿" in problem or "掉帧" in problem:

            causes.append(
                "系统资源占用可能较高"
            )

            causes.append(
                "显卡性能或驱动设置可能存在影响"
            )

            steps.append(
                "查看游戏运行时 CPU 和 GPU 占用率"
            )

            steps.append(
                "查看运行时内存占用"
            )

            steps.append(
                "确认游戏画面设置"
            )

            suggestions.append(
                "降低游戏画面设置"
            )

            suggestions.append(
                "关闭不必要的后台程序"
            )


        # =========================
        # 没有匹配到规则
        # =========================

        if not causes:

            causes.append(
                "目前提供的信息不足，暂时无法确定具体原因"
            )

            steps.append(
                "提供 Windows 版本"
            )

            steps.append(
                "提供软件或游戏名称及版本"
            )

            steps.append(
                "提供完整的错误提示或截图"
            )

            suggestions.append(
                "补充更多故障现象后再进行进一步分析"
            )


        # =========================
        # 去除重复内容
        # =========================

        causes = list(dict.fromkeys(causes))

        steps = list(dict.fromkeys(steps))

        suggestions = list(dict.fromkeys(suggestions))


        summary = (
            "当前使用本地 Demo 模式，"
            "根据故障描述进行了规则分析。"
        )


        # =========================
        # 保存完整记录
        # =========================

        save_diagnosis(
            problem,
            summary,
            causes,
            steps,
            suggestions,
            "Demo"
        )


        return jsonify({

            "summary": summary,

            "causes": causes,

            "steps": steps,

            "suggestions": suggestions,

            "mode": "Demo"

        })


# =========================
# 历史记录
# =========================

@app.route("/history", methods=["GET"])
def history():

    conn = sqlite3.connect("diagnosis.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            problem,
            summary,
            causes,
            steps,
            suggestions,
            mode,
            created_at
        FROM diagnosis_history
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()


    history_list = []


    for record in records:

        try:
            causes = json.loads(record["causes"])
        except:
            causes = []

        try:
            steps = json.loads(record["steps"])
        except:
            steps = []

        try:
            suggestions = json.loads(record["suggestions"])
        except:
            suggestions = []


        history_list.append({

            "id": record["id"],

            "problem": record["problem"],

            "summary": record["summary"],

            "causes": causes,

            "steps": steps,

            "suggestions": suggestions,

            "mode": record["mode"],

            "created_at": record["created_at"]

        })


    return jsonify(history_list)


# =========================
# 删除历史记录
# =========================

@app.route(
    "/history/<int:record_id>",
    methods=["DELETE"]
)
def delete_history(record_id):

    conn = sqlite3.connect("diagnosis.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM diagnosis_history WHERE id = ?",
        (record_id,)
    )

    deleted_count = cursor.rowcount

    conn.commit()

    conn.close()


    if deleted_count == 0:

        return jsonify({
            "success": False,
            "message": "没有找到这条记录"
        }), 404


    return jsonify({
        "success": True,
        "message": "记录删除成功"
    })


# =========================
# 启动 Flask
# =========================

if __name__ == "__main__":

    app.run(debug=True)