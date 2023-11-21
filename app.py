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


tab1, tab2, tab3 = st.tabs(["Dashboard", "Sales Trend Analysis", "Avocado Apocalypse"])

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

        ## Chart
        sub_df1 = dataset3[
            (dataset3["year"]<=select_year_to) 
            & (dataset3["year"]>=select_year_from)  
            & (dataset3["region"]!="Total U.S.")
            & (dataset3["type"]!="all")][["region","type","TotalVolume"]]
        sub_df1 = sub_df1.groupby(["region","type"])["TotalVolume"].sum()
        sub_df1 = pd.DataFrame(sub_df1).reset_index()

        bar = alt.Chart(sub_df1).mark_bar().encode(
            y=alt.X("region:N", title="Geography", sort='-x'),
            x=alt.Y("sum(TotalVolume):Q", title="Total Volume", axis=alt.Axis(labelAngle=-90)),
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
                & (dataset3["type"]!="all")][["region","4046","4225","4770"]]
            sub_df3 = sub_df3.groupby(["region"])[["4046","4225","4770"]].sum()
            sub_df3= sub_df3.rename(columns={"4046": "4046 (~3-5 oz)", "4225":"4225 (~8-10 oz)", "4770":"4770 (~10-15 oz)"})
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



# Dashboard
with tab2:
    ## Title
    st.title('Sales Trend Analysis')

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
                width=1300,
                height=400
            )
    st.altair_chart(fig)

    st.write('''
        At a glance, sales of avocados in US has an uptrend since 2015. The sales pattern also repeats every year. Let's find out
        how the pattern repeats and when do the sales peak occur every year.
    ''')

    st.write('''
        First, let's see how many monthly sales had happened every year.
    ''')

    # Chart 7a (table preparation)
    sub_df7 = dataset3[
        (dataset3["region"]=="Total U.S.")
        & (dataset3["type"]=="all")][["Date","year","region","type","TotalVolume"]]
    sub_df7["month_num"] = sub_df7["Date"].dt.strftime('%m').astype(int)
    sub_df7["month_name"] = sub_df7["Date"].dt.month_name()
    sub_df7

    # Chart 8 (table preview)
    sub_df8 = sub_df7.groupby(["year","month_num","month_name"])["TotalVolume"].sum().reset_index()
    sub_df8 = sub_df8.pivot(index=["month_num","month_name"], columns="year", values="TotalVolume").reset_index()
    sub_df8 = sub_df8.drop(columns=["month_num"])
    sub_df8

    # Chart 7b (chart preview)
    line4 = alt.Chart(sub_df7).mark_line().encode(
        x=alt.X("month_num:O", title="Month", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("sum(TotalVolume):Q", title="Total Volume Sold"),
        color="year:N"
    )
    fig = (line4).configure_axis(
                labelFontSize=10
            ).properties(
                title=('Avocado Sales Volume Comparison'),
                width=1300,
                height=400
            )
    st.altair_chart(fig)
    

# st.write('Year from selected:', select_year_from)
# st.write('Year to selected:', select_year_to)
# st.write('Region selected:', select_region)
# st.write('Type selected:', select_type)
# st.write('Last date:', dataset3[dataset3["year"]==select_year_to]["Date"].max())
# st.write('Last avg price:', avg_price_today)
# st.write('Max price:', avg_price_max)
# st.write('Min price:', avg_price_min)
# st.write('Total Volume:', dataset3[
#     (dataset3["year"]<=select_year_to) 
#     & (dataset3["year"]>=select_year_from)  
#     & (dataset3["region"]=="All Region")
#     & (dataset3["type"]!="all")][["region","type","TotalVolume"]].groupby(["region","type"])["TotalVolume"].sum())



# # Visualization using streamlit
# st.write('''
#     QS World University Rankings include almost 1,500 institutions or universities from around the world. 
#     It's not just iconic institutions that take the top spots. There are universities from 
#     diverse locations across Europe, Asia and North America. The rankings are the fast and 
#     easy way to compare institutions on a host of 8 different criteria: from academic reputation 
#     to the number of international students enrolled. 

#     Now let's look at these universities.
# ''')
# st.write(dataset3.head(10))