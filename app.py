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


tab1, tab2, tab3 = st.tabs(["Dashboard", "Sales & Price Analysis", "Reference"])

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
    total_volume = dataset3[
        (dataset3["year"]<=select_year_to) 
        & (dataset3["year"]>=select_year_from)  
        & (dataset3["region"]==select_region)
        & (dataset3["type"]==select_type)]["TotalVolume"].sum()

    
    col1, col2 = st.columns([2,3])
    with col1:
        st.header("Avocado Average Price")
        st.metric("Total Volume", f'{round(total_volume,0):,}')
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

    st.header("Avocado Sales Volume")

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
                width=1300,
                height=500
            )
    st.altair_chart(fig)
        
    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 14
        sub_df14 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]!="all")][["Date","region","type","year","TotalVolume"]]
        sub_df14 = sub_df14.groupby(["year","type"])["TotalVolume"].sum()
        sub_df14 = pd.DataFrame(sub_df14).reset_index()
        sub_df14a = sub_df14.groupby(["year"])["TotalVolume"].sum()
        sub_df14a = pd.DataFrame(sub_df14a).reset_index()
        sub_df14a= sub_df14a.rename(columns={"TotalVolume": "Percentage"})
        sub_df14 = sub_df14.merge(sub_df14a, on="year", how="left")
        sub_df14["Percentage"] = sub_df14["TotalVolume"] / sub_df14["Percentage"]

        bar = alt.Chart(sub_df14).mark_bar().encode(
            x=alt.X("type:N", title="Type", sort='x', axis=None),
            y=alt.Y("sum(TotalVolume):Q", title="Total Volume"),
            color=alt.Color("type:N", title="Type"),
            column="year:O"
        )
        fig = (bar).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Annual Avocado Sales Volume by Type'),
                    width=75,
                    height=200
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            There are two types of avocado sold in US, conventional and organic. 
            This sales uptrend is dominated by the conventional type. 
            Over 95% avocado sales in US are from this type.
        ''')

    ## Chart 12
    sub_df12 = dataset3[
        (dataset3["year"]<=2020) 
        & (dataset3["year"]>=2015)  
        & (dataset3["region"]!="Total U.S.")
        & (dataset3["type"]=="all")][["region","type","TotalVolume"]]
    sub_df12 = sub_df12.groupby(["region","type"])["TotalVolume"].sum()
    sub_df12 = pd.DataFrame(sub_df12).reset_index().sort_values("TotalVolume", ascending=False)
    sub_df12["cumperc"] = sub_df12["TotalVolume"].cumsum()/sub_df12["TotalVolume"].sum()
    sub_df12 = sub_df12.sort_values("cumperc", ascending=True)
    sort_order = sub_df12["region"].tolist()
    topn_region = sub_df12[sub_df12["cumperc"]<=0.81]
    topn_region = topn_region["region"]

    base = alt.Chart(sub_df12).encode(
            x = alt.X("region:O",sort=sort_order),
        ).properties(
            width = 1300
        )
    bars = base.mark_bar(size = 15).encode(
            y = alt.Y("TotalVolume:Q"),
        ).properties(
            width = 1300
        )
    line = base.mark_line(
            strokeWidth= 2,
            color = "#cb4154" 
        ).encode(
            y=alt.Y('cumperc:Q', title='Cumulative Sum', axis=alt.Axis(format=".0%")),
            text = alt.Text('cumperc:Q')
        )
    points = base.mark_circle(
            strokeWidth= 3,
            color = "#cb4154" 
        ).encode(
            y=alt.Y('cumperc:Q', axis=None)
        )
    
    fig = (bars+line+points).configure_axis(
                labelFontSize=10
            ).properties(
                title='Avocado Sales Volume by Geography',
                width=1300,
                height=500
            ).resolve_scale(y='independent')
    st.altair_chart(fig)
    
    col1, col2 = st.columns([3,2])
    with col1:
        # Chart 13
        sub_df13 = sub_df12[sub_df12["region"].isin(topn_region)]

        base = alt.Chart(sub_df13).encode(
                y = alt.X("region:O",sort=sort_order),
            ).properties(
                width = 800
            )
        bars = base.mark_bar(size = 15).encode(
                x = alt.Y("TotalVolume:Q"),
            ).properties(
                width = 800
            )
        line = base.mark_line(
                strokeWidth= 2,
                color = "#cb4154" 
            ).encode(
                x=alt.Y('cumperc:Q', title='Cumulative Sum', axis=alt.Axis(format=".0%")),
                text = alt.Text('cumperc:Q')
            )
        points = base.mark_circle(
                strokeWidth= 3,
                color = "#cb4154" 
            ).encode(
                x=alt.Y('cumperc:Q', axis=None)
            )
        point_text = points.mark_text(
                align='left',
                baseline='middle',
                dx=-10, 
                dy = -10,
            ).encode(
                x=alt.Y('cumperc:Q', axis=None),
                text=alt.Text('cumperc:Q', format="0.0%"),
                color= alt.value("#cb4154")
            )
        
        fig = (bars+line+points+point_text).configure_axis(
                    labelFontSize=10
                ).properties(
                    title='Avocado Sales Volume by Geography (in 80% sales)',
                    width=800,
                    height=500
                ).resolve_scale(x='independent')
        st.altair_chart(fig)
    with col2:
        st.write('''
            Let's breakdown the sales by its region. West has the most sales among the other region.
            Its sales contribute 10.8% sales of all sales in US. On the second and third place there are South Central and California.
            These 3 regions each has contribute in sales over 10%. 
                 
            Use the pareto principle, then there will be 17 regions that contribute 80% sales of all sales in US.
                 
        ''')

    st.header("Avocado Average Price")

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
            y=alt.Y("sum(AveragePrice):Q", title="Average Price"),
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
            Chart beside illustrate the avocado average price history by its type.
            It shows that average price for the organic type is higher than the conventional type.
            The price of conventional type move around 0.8 until 1.6, while the price of the organic type
            move higher (around 1.2 until 2.1)
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 11
        sub_df11 = dataset3[
            ((dataset3["region"]=="Total U.S.") | (dataset3["region"].isin(topn_region.head(8))))       # atur jumlah region
            & (dataset3["type"]!="all")][["Date","region","type","year","AveragePrice"]]
        sub_df11 = pd.DataFrame(sub_df11).reset_index()

        box1 = alt.Chart(sub_df11).mark_boxplot(extent='min-max', size=20).encode(
            x=alt.X("type:N", axis=None),
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
            From the chart before, region can be ranked by its avocado sales volume. 
            The top 8 region with the highest sales are West, South Central, California, Northeast, Southeast,
            Great Lakes, Midsouth, and Los Angeles.
            
            This chart shows distribution of avocado average price in top 8 region and Total U.S. in overall.
            The median of organic type average price in all region always higher than conventional type average price.
            The median of average price in Total U.S. is 1.55 for organic type and 1.05 for conventional type.
        ''')

    col1, col2 = st.columns([3,2])
    with col1:
        ## Chart 9
        sub_df9 = dataset3[
            (dataset3["region"]=="Total U.S.")
            & (dataset3["type"]!="all")][["Date","region","type","TotalVolume","AveragePrice"]]
        sub_df9 = sub_df9.groupby(["Date","type"])[["TotalVolume","AveragePrice"]].sum()
        sub_df9 = pd.DataFrame(sub_df9).reset_index()

        scatter1 = alt.Chart(sub_df9).mark_point(size=20).encode(
            x=alt.X("AveragePrice:Q", title="Total Volume Sold", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("TotalVolume:Q", title="Average Price Sold"),
            color="type:N"
        )
        fig = (scatter1).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume vs Price'),
                    width=800,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        st.write('''
            Now see how the average price of avocado affect the volume sold.
            The graph shows the distribution of price-volume data pairs.
            At glance, the conventional type has a negative correlation and the organic type has a flatter pattern.
            But this view is still affected by the axis scale.
            Let's see these patterns in separeted chart.
        ''')

    col1, col2, col3 = st.columns([3,3,4])
    with col1:
        ## Chart 15a
        scatter15a = alt.Chart(sub_df9[sub_df9["type"]=="conventional"]).mark_point(size=20).encode(
            x=alt.X("AveragePrice:Q", title="Total Volume Sold", axis=alt.Axis(labelAngle=-45)).scale(zero=False),
            y=alt.Y("TotalVolume:Q", title="Average Price Sold").scale(zero=False)
        )
        final_plot = scatter15a + scatter15a.transform_regression("AveragePrice","TotalVolume").mark_line(color="red")
        fig = (final_plot).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume vs Price (Conventional Type)'),
                    width=400,
                    height=400
                )
        st.altair_chart(fig)
    with col2:
        ## Chart 15b
        scatter15a = alt.Chart(sub_df9[sub_df9["type"]=="organic"]).mark_point(size=20).encode(
            x=alt.X("AveragePrice:Q", title="Total Volume Sold", axis=alt.Axis(labelAngle=-45)).scale(zero=False),
            y=alt.Y("TotalVolume:Q", title="Average Price Sold").scale(zero=False)
        )
        final_plot = scatter15a + scatter15a.transform_regression("AveragePrice","TotalVolume").mark_line(color="red")
        fig = (final_plot).configure_axis(
                    labelFontSize=10
                ).properties(
                    title=('Avocado Sales Volume vs Price (Organic Type)'),
                    width=400,
                    height=400
                )
        st.altair_chart(fig)
    with col3:
        st.write('''
            Separate the data into one type each graph like charts beside.
            The pattern from these charts is not much different from the chart above.
            Red lines show the regression line of the data.
            Conventional and organic type both have negative slope of regression line.
            It means the higher average price of avocado, the less amount volume sold of avocado.
                 
            The organic type has flatter regression line compared to the conventional type's.
            In elasticity term, the organic type is more elastic than the conventional type.
            A little price change in organic type has more effect on volume sold.
        ''')

with tab3:
    # Link to source data
    st.write("Data collected from Kaggle : Avocado Prices (2020)")
    st.link_button("Link", "https://www.kaggle.com/datasets/timmate/avocado-prices-2020")