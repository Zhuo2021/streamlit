import streamlit as st
import pandas as pd
import plotly.express as px

# 设置页面标题
st.title("黄埔分公司数据可视化系统")

# 文件上传组件，让用户上传Excel文件
uploaded_file = st.file_uploader("请上传Excel文件", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # 读取Excel文件内容到DataFrame
        df = pd.read_excel(uploaded_file)

        # 获取第一行数据作为列名选项（假设第一行就是列名所在行，一般Excel文件也是如此）
        column_options = df.columns.tolist()

        # 让用户选择作为横坐标的列，使用下拉菜单展示选项
        selected_x_column = st.selectbox("请选择作为横坐标的列", column_options)

        # 初始化筛选条件列表和筛选列下拉菜单选项列表
        filter_conditions = []
        filter_column_options = column_options.copy()

        # 循环添加筛选条件，直到用户点击停止添加按钮
        while True:
            st.write("### 添加筛选条件")
            # 让用户选择用于筛选数据的列，使用下拉菜单展示选项
            selected_filter_column = st.selectbox("请选择用于筛选数据的列", filter_column_options)
            if selected_filter_column in df.columns:
                # 获取筛选列的所有唯一值作为筛选选项
                filter_options = df[selected_filter_column].unique().tolist()
                # 让用户选择筛选条件，使用下拉菜单展示选项
                selected_filter_value = st.selectbox(f"请选择{selected_filter_column}的筛选条件", filter_options)
                # 将筛选条件添加到列表中
                filter_conditions.append((selected_filter_column, selected_filter_value))
                # 从下拉菜单选项中移除已选的筛选列，避免重复选择
                filter_column_options.remove(selected_filter_column)
            else:
                st.warning(f"Excel文件中不存在名为 {selected_filter_column} 的列，请重新选择。")

            # 提供按钮让用户决定是否继续添加筛选条件，添加了key参数来保证唯一性
            add_another_filter = st.button("添加另一个筛选条件", key=f"add_filter_{len(filter_conditions)}")
            if not add_another_filter:
                break

        # 根据筛选条件对数据进行筛选
        filtered_df = df.copy()
        for column, value in filter_conditions:
            filtered_df = filtered_df[filtered_df[column] == value]

        # 使用value_counts方法统计每个名字出现的次数（基于筛选后的数据）
        name_counts = filtered_df[selected_x_column].value_counts()

        # 将结果转换为DataFrame，方便后续操作
        result_df = name_counts.reset_index()
        result_df.columns = [selected_x_column, 'count']  # 重命名列

        # 让用户选择可视化图表类型，提供柱状图、折线图、圆饼图三个选项
        chart_type = st.selectbox("请选择可视化图表类型", ["柱状图", "折线图", "圆饼图"])

        if chart_type == "柱状图":
            fig = px.bar(result_df, x=selected_x_column, y='count',
                         labels={selected_x_column: selected_x_column, 'count': '总条数'},
                         title=f"{selected_x_column} 对应的总条数统计（筛选条件：{filter_conditions}）")
        elif chart_type == "折线图":
            fig = px.line(result_df, x=selected_x_column, y='count',
                          labels={selected_x_column: selected_x_column, 'count': '总条数'},
                          title=f"{selected_x_column} 对应的总条数统计（筛选条件：{filter_conditions}）")
        elif chart_type == "圆饼图":
            fig = px.pie(result_df, names=selected_x_column, values='count',
                         title=f"{selected_x_column} 对应的占比情况统计（筛选条件：{filter_conditions}）")

        # 在Streamlit中展示绘制好的、可交互的图表
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"读取或可视化数据时出现错误: {str(e)}")