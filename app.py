## Avocado
# Import Libraries
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import matplotlib.pyplot as plt


# Get the data
dataset = pd.read_csv("avocado-prices/avocado-updated-2020.csv")


# Transform and load data
# dataset = dataset.drop(columns=["Unnamed: 0"])
dataset["Date"] = dataset["Date"].astype("datetime64[ns]")
dataset["TotalPrice"] = dataset["Total Volume"] * dataset["AveragePrice"]
cols = dataset.columns.tolist()

## AveragePrice all type for each region
dataset_all_type = dataset.copy()
dataset_all_type = dataset_all_type.groupby(["Date","region","year"])[["Total Volume","4046","4225","4770","Total Bags","Small Bags","Large Bags","XLarge Bags","TotalPrice"]].sum().reset_index()
dataset_all_type["AveragePrice"] = dataset_all_type["TotalPrice"] / dataset_all_type["Total Volume"]
dataset_all_type.insert(1,"type","all")
dataset_all_type = dataset_all_type[cols]
## Union dataset_all_type
dataset3 = pd.concat([dataset, dataset_all_type])
dataset3= dataset3.rename(columns={"Total Volume": "TotalVolume"})


# Set page config
st.set_page_config(layout='wide')


tab1, tab2, tab3 = st.tabs(["Dashboard", "Sales & Price Analysis", "Avocado Apocalypse"])

# Dashboard
with tab1:
    ## Title
    st.title('Avocado Sales in US')

    # region_list = sorted(dataset3['region'].unique())
    # st.write(np.searchsorted(region_list, "TotalUS").astype(int).dtype)

    ## Variable selection
    col1, col2 = st.columns(2)
    with col1:
        select_year_from = st.selectbox(
                'Year from',
                sorted(dataset3['year'].unique()),
                index=0,
                key=1
            )
        select_year_to = st.selectbox(
                'Year to',
                sorted(dataset3['year'].unique()),
                index=5,
                key=2
            )
    with col2:
        select_region = st.selectbox(
                'Select geography',
                sorted(dataset3['region'].unique()),
                index=51,
                key=3
            )
        select_type = st.selectbox(
                'Select type',
                sorted(dataset3['type'].unique()),
                index=0,
                key=4
            )

    avg_price_today = dataset3[
        (dataset3["Date"]==dataset3[dataset3["year"]==select_year_to]["Date"].max()) 
        & (dataset3["region"]==select_region)
        & (dataset3["type"]==select_type)]["AveragePrice"].max()
    avg_price_max = dataset3[
        (dataset3["year"]<=select_year_to) 
        & (dataset3["year"]>=select_year_from)  
        & (dataset3["region"]==select_region)
        & (dataset3["type"]==select_type)]["AveragePrice"].max()
    avg_price_min = dataset3[
        (dataset3["year"]<=select_year_to) 
        & (dataset3["year"]>=select_year_from)  
        & (dataset3["region"]==select_region)
        & (dataset3["type"]==select_type)]["AveragePrice"].min()

    col1, col2 = st.columns([2,3])
    with col1:
        st.header("Avocado Average Price")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Lowest", round(avg_price_min,2))
        with col4:
            st.metric("Highest", round(avg_price_max,2))
        with col5:
            st.metric("Latest", round(avg_price_today,2))

        ## Chart 1
        sub_df1 = dataset3[
            (dataset3["year"]<=select_year_to) 
            & (dataset3["year"]>=select_year_from)  
            & (dataset3["region"]!="Total U.S.")
            & (dataset3["type"]!="all")][["region","type","TotalVolume"]]
        sub_df1 = sub_df1.groupby(["region","type"])["TotalVolume"].sum()
        sub_df1 = pd.DataFrame(sub_df1).reset_index()

        bar = alt.Chart(sub_df1).mark_bar().encode(
            y=alt.X("region:N", title="Geography", sort='-x'),
            x=alt.Y("sum(TotalVolume):Q", title="Total Volume", axis=alt.Axis(labelAngle=-45)),
            color=alt.Color("type:N", title="Type")
        )
        fig = (bar).configure_axis(
                    labelFontSize=10
                ).properties(
                    title='Avocado Sales Volume by Geography',
                    width=500,
                    height=1200
                )
        st.altair_chart(fig)
    with col2:
        col3, col4 = st.columns(2)
        with col3:
            ## Chart 2
            sub_df2 = dataset3[
                (dataset3["year"]<=select_year_to) 
                & (dataset3["year"]>=select_year_from)  
                & (dataset3["region"]==select_region)
                & (dataset3["type"]!="all")][["region","type","TotalVolume"]]
            sub_df2 = sub_df2.groupby(["region","type"])["TotalVolume"].sum()
            sub_df2 = pd.DataFrame(sub_df2).reset_index()

            pie = alt.Chart(sub_df2).mark_arc(innerRadius=50,outerRadius=120).encode(
                theta="TotalVolume",
                color="type:N",
            )
            fig = (pie).configure_axis(
                        labelFontSize=10
                    ).properties(
                        title='Avocado Sales Volume by Type',
                        width=400,
                        height=400
                    )
            st.altair_chart(fig)
        with col4:
            ## Chart 3
            sub_df3 = dataset3[
                (dataset3["year"]<=select_year_to) 
                & (dataset3["year"]>=select_year_from)  
                & (dataset3["region"]==select_region)
                & (dataset3["type"]!="all")][["region","4046","4225","4770","Total Bags"]]
            sub_df3 = sub_df3.groupby(["region"])[["4046","4225","4770","Total Bags"]].sum()
            sub_df3= sub_df3.rename(columns={"4046": "4046 (~3-5 oz)", "4225":"4225 (~8-10 oz)", "4770":"4770 (~10-15 oz)", "Total Bags":"Other"})
            sub_df3 = pd.melt(sub_df3)
            sub_df3= sub_df3.rename(columns={"variable": "size", "value":"TotalVolume"})
            sub_df3 = pd.DataFrame(sub_df3).reset_index()

            pie = alt.Chart(sub_df3).mark_arc(innerRadius=50,outerRadius=120).encode(
                theta="TotalVolume",
                color="size:N",
            )
            fig = (pie).configure_axis(
                        labelFontSize=10
                    ).properties(
                        title='Avocado Sales Volume by Size',
                        width=400,
                        height=400
                    )
            st.altair_chart(fig)

        ## Chart 4
        sub_df4 = dataset3[
            (dataset3["year"]<=select_year_to) 
            & (dataset3["year"]>=select_year_from)  
            & (dataset3["region"]==select_region)
            & (dataset3["type"]==select_type)][["Date","region","type","TotalVolume"]]
        sub_df4 = sub_df4.groupby(["Date"])["TotalVolume"].sum()
        sub_df4 = pd.DataFrame(sub_df4).reset_index()

        line1 = alt.Chart(sub_df4).mark_line().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
            y=alt.Y("sum(TotalVolume):Q", title="Total Volume Sold")
        )
        fig = (line1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume History'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
        
        ## Chart 5
        sub_df5 = dataset3[
            (dataset3["year"]<=select_year_to) 
            & (dataset3["year"]>=select_year_from)  
            & (dataset3["region"]==select_region)
            & (dataset3["type"]==select_type)][["Date","region","type","AveragePrice"]]
        sub_df5 = sub_df5.groupby(["Date"])["AveragePrice"].sum()
        sub_df5 = pd.DataFrame(sub_df5).reset_index()

        line2 = alt.Chart(sub_df5).mark_line().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
            y=alt.Y("sum(AveragePrice):Q", title="Average Price per Avocado Sold")
        )
        fig = (line2).configure_axis(
                    labelFontSize=10
                ).properties(
                    title='Average Price History',
                    width=800,
                    height=400
                )
        st.altair_chart(fig)



# Sales & Price Analysis
with tab2:
    ## Title
    st.title('Sales & Price Analysis')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 6
        sub_df6 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]=="all")][["Date","region","type","TotalVolume"]]
        sub_df6 = sub_df6.groupby(["Date"])["TotalVolume"].sum()
        sub_df6 = pd.DataFrame(sub_df6).reset_index()

        line3 = alt.Chart(sub_df6).mark_line().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
            y=alt.Y("sum(TotalVolume):Q", title="Total Volume Sold")
        )
        fig = (line3).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume History'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            At a glance, sales of oraganic and conventional avocados in US has an uptrend since 2015. 
            The sales pattern tends to increase from beginning of the year until mid year. 
            Then it tends to decrease until the end of year. This pattern repeats every year.
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        # Chart 7
        sub_df7 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]=="all")][["Date","year","region","type","TotalVolume"]]
        sub_df7["month_date"] = sub_df7["Date"].dt.strftime('%m/%d')
        sub_df7["month_num"] = sub_df7["Date"].dt.strftime('%m').astype(int)
        sub_df7["month_name"] = sub_df7["Date"].dt.month_name()

        line4 = alt.Chart(sub_df7).mark_line().encode(
            x=alt.X("month_date:O", title="Month/Date", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("sum(TotalVolume):Q", title="Total Volume Sold"),
            color="year:N"
        )
        fig = (line4).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Annual Sales Volume Comparison'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            If the sales pattern is rearrenged as beside, it shows the high sales peak.
            There are two high sales peaks happen every year, on around early February and early May.
            Meanwhile, sales is at the lowest on around late November.
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 12
        sub_df12 = dataset3[
            (dataset3["year"]<=2020) 
            & (dataset3["year"]>=2015)  
            & (dataset3["region"]!="Total U.S.")
            & (dataset3["type"]=="all")][["region","type","TotalVolume"]]
        sub_df12 = sub_df12.groupby(["region","type"])["TotalVolume"].sum()
        sub_df12 = pd.DataFrame(sub_df12).reset_index().sort_values("TotalVolume", ascending=False).head(8)
        topn_region = sub_df12["region"]

        bar = alt.Chart(sub_df12).mark_bar().encode(
            y=alt.X("region:N", title="Geography", sort='-x'),
            x=alt.Y("sum(TotalVolume):Q", title="Total Volume", axis=alt.Axis(labelAngle=-45))
        )
        fig = (bar).configure_axis(
                    labelFontSize=10
                ).properties(
                    title='Avocado Sales Volume by Geography',
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Top N regioin by sales
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 8
        sub_df8 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]!="all")][["Date","region","type","TotalVolume"]]
        sub_df8 = sub_df8.groupby(["Date","type"])["TotalVolume"].sum()
        sub_df8 = pd.DataFrame(sub_df8).reset_index()

        line1 = alt.Chart(sub_df8).mark_line().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
            y=alt.Y("sum(TotalVolume):Q", title="Total Volume Sold"),
            color="type:N"
        )
        fig = (line1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume History by Type'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Tren sales yang naik didiominasi oleh conventional. Sekitar xx% sales adalah conventional
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 10
        sub_df10 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]!="all")][["Date","region","type","AveragePrice"]]
        sub_df10 = sub_df10.groupby(["Date","type"])["AveragePrice"].sum()
        sub_df10 = pd.DataFrame(sub_df10).reset_index()

        line1 = alt.Chart(sub_df10).mark_line().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
            y=alt.Y("sum(AveragePrice):Q", title="Total Volume Sold"),
            color="type:N"
        )
        fig = (line1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Average Price History by Type'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Tren harga alpukat
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 11
        sub_df11 = dataset3[
            ((dataset3["region"]=="Total U.S.") | (dataset3["region"].isin(topn_region)))
            & (dataset3["type"]!="all")][["Date","region","type","year","AveragePrice"]]
        sub_df11 = pd.DataFrame(sub_df11).reset_index()

        box1 = alt.Chart(sub_df11).mark_boxplot(extent='min-max', size=20).encode(
            x=alt.X("type:N"),
            y=alt.Y("AveragePrice:Q", title="Average Price"),
            color="type:N",
            column=alt.Column('region:N')
        )
        fig = (box1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Average Price Comparison'),
                    width=50,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Perbandingan harga rata-rata
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 9
        sub_df9 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]!="all")][["Date","region","type","TotalVolume","AveragePrice"]]
        sub_df9 = sub_df9.groupby(["Date","type"])[["TotalVolume","AveragePrice"]].sum()
        sub_df9 = pd.DataFrame(sub_df9).reset_index()

        scatter1 = alt.Chart(sub_df9).mark_circle(size=20).encode(
            x=alt.X("AveragePrice:Q", title="Total Volume Sold", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("TotalVolume:Q", title="Average Price Sold"),
            column="type:N"
        )
        fig = (scatter1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume vs Price Elasticity'),
                    width=300,
                    height=300
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Elastisitas penjualan
        ''')