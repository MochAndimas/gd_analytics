"""functions file dashboard"""

from __future__ import division
import time
import json
import io
import requests
import pandas as pd
import csv
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import date
from apps import db
from sqlalchemy import desc, asc
from apps.authentication.models import GooddreamerNovel as gn, GooddreamerUserNovelProgression as gunp, GooddreamerNovelTransaction as gnt
from apps.authentication.models import GooddreamerTransactionDetails as gtd, GooddreamerTransaction as gt, DataCategory as dc
from apps.authentication.models import PivotNovelCategory as pnc, Account as ac, AppsflyerAggregatedData as aad
from decouple import config


DEBUG = config('DEBUG', default=True, cast=bool)
API_KEY = "eyJhbGciOiJBMjU2S1ciLCJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwidHlwIjoiSldUIiwiemlwIjoiREVGIn0.lDtMMOAHflCVpKgMGT-YoGcoye63SVLaPFtELQMDwW-S3r_sDJPJeg._VsaR7Cznd1wABto.DYNLvy86hQQbR4QQR0QTdIbipaZjr1EBDDQ3m-lHsIhbGhPSS8Zp3WDu0tsT1drd49-eU3Ek08LcdRM5V1z0zCZxurcFMmT4o1tpLZqOFHa85Ypj9-pTPpzVUNYN0Q7BAx9eXq7AHbgYtdXiNHeLcYtzam99UzkcaAQFmMlEqPPjRpRPY5eslkbBFX4mpRuIzfwiPFyUoCvs4e1zHjHxSBspIj5ESvswXZvT7EtvWgIFjLVZewEp-QopSMHyj9PxEm2J0Q5IeO2LfFrADr_z0YD87mKvUcUIHzQW4PjEVhOWvgPqgWjw6NHb_6-TXiWScgXdqKSjc4XxSZDq4X-G-ESzefHPEOZIM_mnKbqMtyNldgST53duL-0fMD0__SM_JJ24wIJXdLRijQpd9YqWf4267qE4b6RXCFL0gNM7UUKCfT52FBN_KANVmXZobhWta438g8qxVxONkTI0f2fBgFZqLmjubPOwiRqIVFZJIX38W0fN5AYjMaimRxmMfvbH_pTXSl2NqhD9bby6bYw.0bdVe3QKqkywFOr43kDzPQ"
APP_ID = "id.gooddreamer.novel"


def get_appsflyer_data(api_token, app_id, start_date, end_date, data_type):
    """
    Retrieves raw data from Appsflyer API and converts it into a Pandas dataframe.

    Parameters:
        api_token (str): Appsflyer API token
        app_id (str): App ID
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        Pandas dataframe: Raw data from Appsflyer API
    """

    # Set API endpoint URL
    endpoint = f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/{data_type}/v5?from={start_date}&to={end_date}&reattr=false&additional_fields=device_category"

    # Set request headers
    headers = {
        "authorization": api_token,
        "accept": "text/csv"
    }
    if DEBUG:
        response = None
    else:
        # Send API request
        response = requests.get(endpoint, headers=headers)

        # Convert response content into Pandas dataframe and save into csv
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        df.to_csv(f'update_{data_type}.csv', index=False)

    # parsing colum date
    dates_col = ["Install Time"]
    pars_date = pd.read_csv(f'./{data_type}.csv', index_col=False, parse_dates=dates_col, low_memory=False)
    df = pd.DataFrame(pars_date)

    # format datetime into date only
    last1days = datetime.datetime.today() - datetime.timedelta(1)
    last1days_date = last1days.date()
    df['Install Time'] = pd.to_datetime(df['Install Time']).dt.date

    # Check if the CSV file already has data for today and append into report file
    if DEBUG is not True:
        if last1days_date in df["Install Time"].values:
            return 'data is uptodate!'
        else:
            with open(f'./update_{data_type}.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                data_to_append = [row for row in reader]
            
            with open(f'./{data_type}.csv', 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(data_to_append[1:])
            return 'data must be updated!'
    else:
        return df


def pembaca_pgnt(from_date='2023-01-01', to_date='2023-02-06'):
    """pagination pembaca novel"""

    query = db.session.query(
        gunp.novel_id.distinct().label('novel_id'),
        gn.novel_title.label('novel_title'),
        db.func.count(gunp.user_id).over(
            partition_by=gunp.novel_id).label('total_pembaca')).join(
        gunp,
        gunp.novel_id == gn.id).filter(db.func.date(gunp.create_at).between(from_date, to_date)).order_by(desc('total_pembaca'))

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Table(header=dict(values=df.columns),
                 cells=dict(values=[df.novel_id, df.novel_title, df.total_pembaca])),
        layout=dict(height=650, width=520)
    )
    fig.update_layout(title='Jumlah Pembaca')
    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def pembeli_pgnt(from_date='2023-01-01', to_date='2023-02-06'):
    """pagination pembeli novel"""

    query = db.session.query(
        gnt.novel_id.distinct().label('novel_id'),
        gn.novel_title.label('novel_title'),
        db.func.count(gnt.user_id).over(
            partition_by=gnt.novel_id).label('total_pembeli')).join(
        gnt, gnt.novel_id == gn.id).filter(db.func.date(gnt.created_at).between(from_date, to_date)).order_by(desc('total_pembeli'))

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Table(header=dict(values=df.columns),
                 cells=dict(values=[df.novel_id, df.novel_title, df.total_pembeli])),
        layout=dict(height=650, width=520)
    )
    fig.update_layout(title='Jumlah Pembeli')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def total_pembaca_month(from_date='2023-01-01', to_date='2023-02-06'):
    """stack chart total pembaca"""

    register_reader = db.session.query(
        db.func.date(gunp.create_at).distinct().label('dates'),
        db.func.count(gunp.id).over(partition_by=db.func.date(
            gunp.create_at)).label('total_pembaca')
    ).join(ac, gunp.user_id == ac.id).filter(ac.is_guest == 0, db.func.date(gunp.create_at).between(from_date, to_date)).order_by(desc('dates'))
    guest_reader = db.session.query(
        db.func.date(gunp.create_at).distinct().label('dates'),
        db.func.count(gunp.id).over(partition_by=db.func.date(
            gunp.create_at)).label('total_pembaca')
    ).join(ac, gunp.user_id == ac.id).filter(ac.is_guest == 1, db.func.date(gunp.create_at).between(from_date, to_date)).order_by(desc('dates'))

    register_reader_df = pd.DataFrame(register_reader)
    guest_reader_df = pd.DataFrame(guest_reader)

    fig = go.Figure(data=[
        go.Bar(name='guest_reader', x=guest_reader_df.dates,
               y=guest_reader_df.total_pembaca, text=guest_reader_df.total_pembaca, textposition='inside'),
        go.Bar(name='register_reader', x=register_reader_df.dates,
               y=register_reader_df.total_pembaca, text=register_reader_df.total_pembaca, textposition='inside')
    ])
    # Change the bar mode
    fig.update_layout(barmode='stack', autosize=True,
                      title='Total Pembaca Novel /Days')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Total Pembaca')
    fig.update_xaxes(dtick='D1')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def total_pembeli_month(from_date='2023-01-01', to_date='2023-02-06'):
    """bar line chart total pembeli /monnth"""

    pembeli_novel = db.session.query(
        db.func.date(gnt.created_at).distinct().label('date'),
        db.func.count(gnt.id).over(partition_by=db.func.date(
            gnt.created_at)).label('total_pembeli')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date)).order_by(asc('date'))

    pembeli_novel_df = pd.DataFrame(pembeli_novel)

    fig = go.Figure(
        [go.Bar(x=pembeli_novel_df.date, y=pembeli_novel_df.total_pembeli, marker=dict(showscale=True, colorscale='bluered_r', color=pembeli_novel_df.total_pembeli))])

    # chart config
    fig.update_layout(
        title='Total Pembeli Novel /Days', showlegend=False)
    fig.update_traces(text=pembeli_novel_df.total_pembeli,
                      textposition='inside')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Total Pembeli')
    fig.update_xaxes(dtick='D1')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def genre_pembeli(from_date='2023-01-01', to_date='2023-02-06'):
    """table pembeli per genre"""

    df = db.session.query(
        dc.category_name.distinct().label('category_name'),
        db.func.count(gnt.id).over(
            partition_by=dc.category_name).label('jumlah_pembeli')
    ).join(pnc, pnc.category_id == dc.id).join(gn, pnc.novel_id == gn.id).join(gnt, gn.id == gnt.novel_id).filter(db.func.date(gnt.created_at).between(from_date, to_date)).order_by(asc('jumlah_pembeli'))

    genre_df = pd.DataFrame(df)

    fig = go.Figure(
        [go.Bar(x=genre_df[:10].jumlah_pembeli,
                y=genre_df[:10].category_name, orientation='h', marker=dict(showscale=True, colorscale='burgyl', color=genre_df[:10].jumlah_pembeli))]
    )

    # chart config
    fig.update_layout(title='Pembeli /Genre')
    fig.update_xaxes(title='jumlah_pembeli')
    fig.update_yaxes(title='category_name')
    fig.update_traces(text=genre_df.jumlah_pembeli, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def genre_pembaca(from_date='2023-01-01', to_date='2023-02-06'):
    """table pembaca per genre"""

    df = db.session.query(
        dc.category_name.distinct().label('category_name'),
        db.func.count(gunp.id).over(
            partition_by=dc.category_name).label('jumlah_pembaca')
    ).join(pnc, pnc.category_id == dc.id).join(gn, pnc.novel_id == gn.id).join(gunp, gn.id == gunp.novel_id).filter(db.func.date(gunp.create_at).between(from_date, to_date)).order_by(asc('jumlah_pembaca'))

    genre_df = pd.DataFrame(df)

    fig = go.Figure(
        [go.Bar(x=genre_df[:10].jumlah_pembaca,
                y=genre_df[:10].category_name, orientation='h', marker=dict(showscale=True, colorscale='burgyl', color=genre_df[:10].jumlah_pembaca))]
    )

    # chart config
    fig.update_layout(title='Pembaca /Genre')
    fig.update_xaxes(title='jumlah_pembaca')
    fig.update_yaxes(title='category_name')
    fig.update_traces(text=genre_df.jumlah_pembaca, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def total_gross_revenue(from_date=None, to_date=None):
    """revenue convert lambda"""

    rv = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)
    df = pd.DataFrame(rv)
    convert_rp = df['revenue'].apply(lambda x: "Rp. {:,f}".format((x)))

    return convert_rp


def total_revenue():
    """revenue convert lambda"""

    rv = db.session.query(
        db.func.sum(gtd.package_price).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at) >= '2023-01-01', gt.transaction_status == 1)
    df = pd.DataFrame(rv)
    convert_rp = df['revenue'].apply(lambda x: "Rp. {:,f}".format((x)))

    return convert_rp


def total_transaksi_coin(from_date='2023-01-01', to_date='2023-02-06'):
    """chart transaksi coin"""

    read_pending = db.session.query(
        db.func.date(gt.created_at).distinct().label('transaction_date'),
        db.func.count(gt.user_id).over(partition_by=db.func.date(
            gt.created_at)).label('transaksi_coin_pending')
    ).filter(gt.transaction_status == 0, db.func.date(gt.created_at).between(from_date, to_date)).order_by(desc('transaction_date'))

    read_success = db.session.query(
        db.func.date(gt.created_at).distinct().label('transaction_date'),
        db.func.count(gt.user_id).over(partition_by=db.func.date(
            gt.created_at)).label('transaksi_coin_success')
    ).filter(gt.transaction_status == 1, db.func.date(gt.created_at).between(from_date, to_date)).order_by(desc('transaction_date'))

    read_expired = db.session.query(
        db.func.date(gt.created_at).distinct().label('transaction_date'),
        db.func.count(gt.user_id).over(partition_by=db.func.date(
            gt.created_at)).label('transaksi_coin_expired')
    ).filter(gt.transaction_status == 2, db.func.date(gt.created_at).between(from_date, to_date)).order_by(desc('transaction_date'))

    read_total = db.session.query(
        db.func.date(gt.created_at).distinct().label('transaction_date'),
        db.func.count(gt.user_id).over(partition_by=db.func.date(
            gt.created_at)).label('total_transaction_coin')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date)).order_by(desc('transaction_date'))

    pending_df = pd.DataFrame(read_pending)
    success_df = pd.DataFrame(read_success)
    expired_df = pd.DataFrame(read_expired)
    total_df = pd.DataFrame(read_total)

    fig = go.Figure(data=[
        # go.Bar(name='Transaksi Coin Pending', x=pending_df.transaction_date,
        # y=pending_df.transaksi_coin_pending),
        go.Bar(name='Transaksi Coin Expired', x=expired_df.transaction_date,
               y=expired_df.transaksi_coin_expired, marker=dict(color='red'), text=expired_df.transaksi_coin_expired, textposition='inside'),
        go.Bar(name='Transaksi Coin Success', x=success_df.transaction_date, y=success_df.transaksi_coin_success, marker=dict(color='green'), text=success_df.transaksi_coin_success, textposition='inside')]
    )

    # config figure
    fig.update_xaxes(autorange=True, title='Transaction Date', dtick='D1')  # ,
    # dtick='M1', tickformat='%b\n%Y')
    fig.update_yaxes(title='Transaction Coin')
    fig.add_traces(go.Scatter(x=total_df.transaction_date, y=total_df.total_transaction_coin,
                   line=dict(color='yellow'), name='Total Trasaction Coin'))
    fig.update_layout(title='Transaction Coin', barmode='group')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def category_coin(from_date='2023-01-01', to_date='2023-02-06'):
    """chart category coin"""

    query = db.session.query(
        db.func.concat(gt.transaction_coin_value).distinct().label(
            'coin_value'),
        db.func.count(gt.user_id).over(
            partition_by=gt.transaction_coin_value).label('total_pembelian')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1).order_by(asc('coin_value'))

    category_df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(y=category_df.coin_value,
               x=category_df.total_pembelian, orientation='h', marker=dict(showscale=True, colorscale='bluered_r', color=category_df.total_pembelian))
    )

    # config figure
    fig.update_layout(title='Transaction coin /Value')
    fig.update_xaxes(title='Total Pembelian')
    fig.update_yaxes(title='Coin Value', categoryorder='array', categoryarray=[
                     1, 10, 20, 25, 29, 40, 75, 100, 120])
    fig.update_traces(text=category_df.total_pembelian, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def revenue_days(from_date='2023-01-01', to_date='2023-02-06'):
    """chart revenue /month"""

    query = db.session.query(
        db.func.date(gt.created_at).distinct().label('date'),
        db.func.sum(gtd.package_price + gtd.package_fee).over(
            partition_by=db.func.date(gt.created_at)).label('total_revenue')
    ).join(gtd, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1).order_by(desc('date'))

    revenue_df = pd.DataFrame(query)

    fig = go.Figure(
        go.Scatter(x=revenue_df.date, y=revenue_df.total_revenue)
    )

    # config figure
    fig.update_layout(title='Total Revenue /Days')
    fig.update_xaxes(title='Months')
    fig.update_yaxes(title='Total Revenue')
    fig.update_traces(text=revenue_df.total_revenue, textposition='top center')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def pembaca_day(from_date='2023-01-01', to_date='2023-02-06'):
    """chart pembaca per day"""

    query = db.session.query(
        db.func.dayname(gunp.create_at).distinct().label('day'),
        db.func.count(gunp.user_id).over(
            partition_by=db.func.dayname(gunp.create_at)).label('total_pembaca')
    ).filter(db.func.date(gunp.create_at).between(from_date, to_date))

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(x=df.total_pembaca, y=df.day, orientation='h', marker=dict(
            showscale=True, colorscale='emrld', color=df.total_pembaca))
    )

    # config figure
    fig.update_layout(title='Pembaca /Day')
    fig.update_yaxes(title='Day', dtick='D1', tickformat='%b', categoryorder='array', categoryarray=[
                     'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig.update_xaxes(title='Total Pembaca')
    fig.update_traces(text=df.total_pembaca, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def pembeli_day(from_date='2023-01-01', to_date='2023-02-06'):
    """chart pembeli per day"""

    query = db.session.query(
        db.func.dayname(gnt.created_at).distinct().label('day'),
        db.func.count(gnt.user_id).over(
            partition_by=db.func.dayname(gnt.created_at)
        ).label('total_pembeli')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date))

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(x=df.total_pembeli, y=df.day, orientation='h', marker=dict(
            showscale=True, colorscale='emrld', color=df.total_pembeli))
    )

    # config fig
    fig.update_layout(title='Pembeli /Day')
    fig.update_yaxes(title='Day', dtick='D1', tickformat='%b', categoryorder='array', categoryarray=[
                     'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig.update_xaxes(title='Total Pembaca')
    fig.update_traces(text=df.total_pembeli, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def daily_growth_pembaca(from_date=None, to_date=None):
    """daily growth pembaca"""

    today = db.session.query(
        db.func.count(gunp.id).label('today')
    ).filter(db.func.date(gunp.create_at) == to_date).scalar()
    yesterday = db.session.query(
        db.func.count(gunp.id).label('yesterday')
    ).filter(db.func.date(gunp.create_at) == from_date).scalar()

    if today == 0:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def daily_growth_pembeli(from_date=None, to_date=None):
    """daily growth pembeli"""

    today = db.session.query(
        db.func.count(gnt.id).label('today')
    ).filter(db.func.date(gnt.created_at) == to_date).scalar()
    yesterday = db.session.query(
        db.func.count(gnt.id).label('yesterday')
    ).filter(db.func.date(gnt.created_at) == from_date).scalar()

    if today == 0:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def daily_growth_coin(transaction_status=0, from_date=None, to_date=None):
    """daily growth coin. 0 = Pending, 1 = Success, 2 = Expired"""

    today = db.session.query(
        db.func.count(gt.id).label('today')
    ).filter(db.func.date(gt.created_at) == to_date, gt.transaction_status == transaction_status).scalar()
    yesterday = db.session.query(
        db.func.count(gt.id).label('yesterday')
    ).filter(db.func.date(gt.created_at) == from_date, gt.transaction_status == transaction_status).scalar()

    if today == 0 or yesterday == 0:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def daily_growth_total_coin():
    """daily growth coin. 0 = Pending, 1 = Success, 2 = Expired"""

    today = db.session.query(
        db.func.count(gt.id).label('today')
    ).filter(db.func.date(gt.created_at) == date.today()).scalar()
    last_1_days = datetime.datetime.today() - datetime.timedelta(1)
    yesterday_date = last_1_days.date()
    yesterday = db.session.query(
        db.func.count(gt.id).label('yesterday')
    ).filter(db.func.date(gt.created_at) == yesterday_date).scalar()

    if today == 0:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def dg_revenue_gross(from_date=None, to_date=None, timedelta=1):
    """daily growth gross revenue"""

    today = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1).scalar()
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta
    yesterday = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at).between(fromdate_lastweek, todate_lastweek), gt.transaction_status == 1).scalar()
    
    if today == None or yesterday == None:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def dg_revenue():
    """daily growth gross revenue"""

    today = db.session.query(
        db.func.sum(gtd.package_price).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at) == date.today(), gt.transaction_status == 1).scalar()
    last_1_days = datetime.datetime.today() - datetime.timedelta(1)
    yesterday_date = last_1_days.date()
    yesterday = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at) == yesterday_date, gt.transaction_status == 1).scalar()

    if today == None or yesterday == None:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return txt


def coin_days(from_date='2023-01-01', to_date='2023-02-06'):
    """pembelian coin per days"""

    query = db.session.query(
        db.func.dayname(gt.created_at).distinct().label('day'),
        db.func.count(gt.id).over(partition_by=db.func.dayname(
            gt.created_at)).label('total_pembelian')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date))

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(y=df.total_pembelian, x=df.day, marker=dict(
            showscale=True, colorscale='emrld', color=df.total_pembelian))
    )

    # config fig
    fig.update_layout(title='Pembelian Coin /Days')
    fig.update_xaxes(title='day', dtick='D1', tickformat='%b', categoryorder='array', categoryarray=[
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    fig.update_yaxes(title='Total Pembelian Coin')
    fig.update_traces(text=df.total_pembelian, textposition='inside')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def dg_register(from_date=None, to_date=None):
    """daily growth register"""
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    week1 = db.session.query(
        db.func.count(ac.id)
    ).filter(db.func.date(ac.registered_at).between(from_date, to_date), ac.is_guest == 0).scalar()

    week2 = db.session.query(
        db.func.count(ac.id)
    ).filter(db.func.date(ac.registered_at).between(fromdate_lastweek, todate_lastweek), ac.is_guest == 0).scalar()

    if week1 == 0 or week2 == 0:
        growth = 0
    else:
        growth = (week1 - week2)/week1

    txt = "{:.0%}".format(growth)

    return txt


def register(from_date=None, to_date=None):
    """total register last week"""

    reg = db.session.query(
        db.func.count(ac.id).label('register')
    ).filter(db.func.date(ac.registered_at).between(from_date, to_date), ac.is_guest == 0)

    return reg


def beli_coin(from_date=None, to_date=None):
    """beli coin last week"""
    beli_coin_w1 = db.session.query(
        db.func.count(gt.user_id).label('beli_coin')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)

    return beli_coin_w1


def beli_coin_unique(from_date=None, to_date=None):
    """beli coin unique"""
    beli_coin_w1 = db.session.query(
        gt.user_id.distinct().label('beli_coin')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)

    df = pd.DataFrame(beli_coin_w1)
    count = df['beli_coin'].count()

    return count


def dg_coin_periods(from_date=None, to_date=None):
    """daily growth pembelian coin"""

    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    w1 = beli_coin(from_date=from_date, to_date=to_date).scalar()
    w2 = beli_coin(from_date=fromdate_lastweek, to_date=todate_lastweek).scalar()

    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def dg_coin_unique_periods(from_date=None, to_date=None):
    """daily growth pembelian coin unique"""
    fromdate_lastweek = from_date - datetime.timedelta(7)
    todate_lastweek = to_date - datetime.timedelta(7) 

    w1 = beli_coin_unique(from_date=from_date, to_date=to_date)
    w2 = beli_coin_unique(from_date=fromdate_lastweek, to_date=todate_lastweek)

    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def beli_novel(from_date=None, to_date=None):
    """beli_novel last week"""
    beli_novel_w1 = db.session.query(
        db.func.count(gnt.user_id).label('beli_novel')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date))

    return beli_novel_w1


def beli_novel_unique(from_date=None, to_date=None):
    """beli_novel last week"""
    beli_novel_w1 = db.session.query(
        gnt.user_id.distinct().label('user')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date))

    df = pd.DataFrame(beli_novel_w1)
    count = df['user'].count()
    
    return count


def dg_novel_periods(from_date=None, to_date=None):
    """daily growth pembelian novel periods"""
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    w1 = beli_novel(from_date=from_date, to_date=to_date).scalar()
    w2 = beli_novel(from_date=fromdate_lastweek, to_date=todate_lastweek).scalar()
    
    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def dg_novel_unique_periods(from_date=None, to_date=None):
    """daily growth pembelian novel periods"""
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    w1 = beli_novel_unique(from_date=from_date, to_date=to_date)
    w2 = beli_novel_unique(from_date=fromdate_lastweek, to_date=todate_lastweek)

    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def dau_mau_chart(from_date='2023-01-09', to_date='2023-02-23'):
    """DAU & MAU chart"""

    df = pd.read_csv('./dau&mau.csv', delimiter=';')
    df['date'] = pd.to_datetime(df['date']).dt.date
    filtered_df = df[(df['date'] >= from_date) & (df['date'] <= to_date)]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=filtered_df.date, y=filtered_df.daily_active_user,
                   name='Daily Active User', mode='lines+markers'),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=filtered_df.date, y=filtered_df.monthly_active_user,
                   name='Monthly Active User', mode='lines+markers'),
        secondary_y=True
    )
    fig.update_layout(title='DAU & MAU /Days')
    fig.update_xaxes(title='Date', dtick='D1')
    fig.update_yaxes(title='Active Users')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def install_chart(from_date=None, to_date=None):
    """install chart"""
    non_organic_csv = pd.read_csv('./installs_report.csv', index_col=False, low_memory=False)
    non_organic_df = pd.DataFrame(non_organic_csv)

    organic_csv = pd.read_csv('./organic_installs_report.csv', index_col=False)
    organic_df = pd.DataFrame(organic_csv)

    non_organic_df['Install Time'] = pd.to_datetime(non_organic_df['Install Time']).dt.date
    organic_df['Install Time'] = pd.to_datetime(organic_df['Install Time']).dt.date

    non_organic_filter = non_organic_df[(non_organic_df['Install Time'] >= from_date)&
                                        (non_organic_df['Install Time'] <= to_date)]
    organic_filter = organic_df[(organic_df['Install Time'] >= from_date)&
                                        (organic_df['Install Time'] <= to_date)] 

    df_non_organic = non_organic_filter.groupby(['Install Time'])['Install Time'].count()
    df_organic = organic_filter.groupby(['Install Time'])['Install Time'].count()

    df_1 = pd.DataFrame(df_non_organic)
    df_2 = pd.DataFrame(df_organic)

    fig = go.Figure(data=[
        go.Bar(x=df_1.index.values, y=df_1['Install Time'], name='Non Organic', text=df_1['Install Time'], textposition='inside'),
        go.Bar(x=df_2.index.values, y=df_2['Install Time'], name='Organic', text=df_2['Install Time'], textposition='inside')
    ])
    fig.update_layout(title='Installs /Days', barmode='stack')
    fig.update_xaxes(title='Date', dtick='D1')
    fig.update_yaxes(title='Total install')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def dau_mau_avg_text(from_date=None, to_date=None, column=None):
    """DAU & MAU text"""

    df = pd.read_csv('./dau&mau.csv', delimiter=';')
    df['date'] = pd.to_datetime(df['date']).dt.date
    w1 = df[(df['date'] >= from_date) & (df['date'] <= to_date)]

    mean = w1[column].mean()

    return mean


def pembaca_pembeli_month(from_date='2023-01-01'):
    """Pembaca pembeli /Month"""

    query_1 = db.session.query(
        db.func.concat(db.func.year(gnt.created_at), '-',
                       db.func.month(gnt.created_at)).distinct().label('periods'),
        db.func.count(gnt.id).over(partition_by=db.func.month(
            gnt.created_at)).label('pembeli_novel')
    ).filter(db.func.date(gnt.created_at) >= from_date)

    query_2 = db.session.query(
        db.func.concat(db.func.year(gunp.create_at), '-',
                       db.func.month(gunp.create_at)).distinct().label('periods'),
        db.func.count(gunp.id).over(partition_by=db.func.month(
            gunp.create_at)).label('pembaca_novel')
    ).filter(db.func.date(gunp.create_at) >= from_date)

    df_pembeli = pd.DataFrame(query_1)
    df_pembaca = pd.DataFrame(query_2)

    fig = go.Figure(data=[
        go.Bar(x=df_pembaca.periods, y=df_pembaca.pembaca_novel,
               text=df_pembaca.pembaca_novel, textposition='outside', name='pembaca_novel'),
        go.Bar(x=df_pembeli.periods, y=df_pembeli.pembeli_novel,
               text=df_pembeli.pembeli_novel, textposition='outside', name='pembeli_novel')
    ])

    fig.update_layout(title='Pembaca & Pembeli /Month')
    fig.update_xaxes(title='Periods', dtick='M1')
    fig.update_yaxes(title='Total')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def revenue_month(from_date='2023-01-01'):
    """revenue /Month chart"""
    query = db.session.query(
        db.func.concat(db.func.year(gt.created_at), '-',
                       db.func.month(gt.created_at)).distinct().label('periods'),
        db.func.sum(gtd.package_price+gtd.package_fee).over(
            partition_by=db.func.month(gt.created_at)).label('revenue')
    ).join(gtd, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at) >= from_date, gt.transaction_status == 1)

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(x=df.periods, y=df.revenue, text=df.revenue.apply(
            lambda x: "Rp. {:,f}".format((x))), textposition='inside')
    )
    fig.update_layout(title='Revenue /Month')
    fig.update_xaxes(title='Periods', dtick='M1')
    fig.update_yaxes(title='Revenue')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def transaction_coin_month(from_date='2023-01-01'):
    """transaction coin /Month"""
    read_success = db.session.query(
        db.func.concat(db.func.year(gt.created_at), '-',
                       db.func.month(gt.created_at)).distinct().label('periods'),
        db.func.count(gt.user_id).over(partition_by=db.func.month(
            gt.created_at)).label('transaksi_coin_success')
    ).filter(gt.transaction_status == 1, db.func.date(gt.created_at) >= from_date).order_by(desc('periods'))

    read_expired = db.session.query(
        db.func.concat(db.func.year(gt.created_at), '-',
                       db.func.month(gt.created_at)).distinct().label('periods'),
        db.func.count(gt.user_id).over(partition_by=db.func.month(
            gt.created_at)).label('transaksi_coin_expired')
    ).filter(gt.transaction_status == 2, db.func.date(gt.created_at) >= from_date).order_by(desc('periods'))

    read_total = db.session.query(
        db.func.concat(db.func.year(gt.created_at), '-',
                       db.func.month(gt.created_at)).distinct().label('periods'),
        db.func.count(gt.user_id).over(partition_by=db.func.month(
            gt.created_at)).label('total_transaction_coin')
    ).filter(db.func.date(gt.created_at) >= from_date).order_by(desc('periods'))

    df_success = pd.DataFrame(read_success)
    df_expired = pd.DataFrame(read_expired)
    df_total = pd.DataFrame(read_total)

    fig = go.Figure(data=[
        go.Bar(x=df_expired.periods, y=df_expired.transaksi_coin_expired, name='coin_expired',
               text=df_expired.transaksi_coin_expired, textposition='inside', marker=dict(color='red')),
        go.Bar(x=df_success.periods, y=df_success.transaksi_coin_success, name='coin_success',
               text=df_success.transaksi_coin_success, textposition='inside', marker=dict(color='green')),
        go.Bar(x=df_total.periods, y=df_total.total_transaction_coin, name='total_transaction',
               text=df_total.total_transaction_coin, textposition='inside', marker=dict(color='blue'))
    ])

    fig.update_layout(title='Transaction Coin /Month')
    fig.update_xaxes(title='Periods')
    fig.update_yaxes(title='Transaction Coin')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def af_installs(from_date=None, to_date=None):
    """af_installs by periods events"""

    last1days = datetime.datetime.today() - datetime.timedelta(1)
    last1days_date = last1days.date()
    
    #update data
    get_appsflyer_data(api_token=API_KEY, app_id=APP_ID, data_type='installs_report', start_date=last1days_date, end_date=last1days_date)
    get_appsflyer_data(api_token=API_KEY, app_id=APP_ID, data_type='organic_installs_report', start_date=last1days_date, end_date=last1days_date)

    non_organic_csv = pd.read_csv('./installs_report.csv', index_col=False, low_memory=False)
    non_organic_df = pd.DataFrame(non_organic_csv)

    organic_csv = pd.read_csv('./organic_installs_report.csv', index_col=False)
    organic_df = pd.DataFrame(organic_csv)

    non_organic_df['Install Time'] = pd.to_datetime(non_organic_df['Install Time']).dt.date
    organic_df['Install Time'] = pd.to_datetime(organic_df['Install Time']).dt.date

    non_organic_filter = non_organic_df[(non_organic_df['Install Time'] >= from_date)&
                                        (non_organic_df['Install Time'] <= to_date)]
    organic_filter = organic_df[(organic_df['Install Time'] >= from_date)&
                                        (organic_df['Install Time'] <= to_date)]

    count = non_organic_filter['Install Time'].count() + organic_filter['Install Time'].count()
    
    return count


def dg_af_installs(from_date=None, to_date=None):
    """daily growth installs"""
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    non_organic_csv = pd.read_csv('./installs_report.csv', index_col=False, low_memory=False)
    non_organic_df = pd.DataFrame(non_organic_csv)

    organic_csv = pd.read_csv('./organic_installs_report.csv', index_col=False)
    organic_df = pd.DataFrame(organic_csv)

    non_organic_df['Install Time'] = pd.to_datetime(non_organic_df['Install Time']).dt.date
    organic_df['Install Time'] = pd.to_datetime(organic_df['Install Time']).dt.date

    non_organic_filter_w1 = non_organic_df[(non_organic_df['Install Time'] >= from_date)&
                                    (non_organic_df['Install Time'] <= to_date)]
    non_organic_filter_w2 = non_organic_df[(non_organic_df['Install Time'] >= fromdate_lastweek)&
                                    (non_organic_df['Install Time'] <= todate_lastweek)]
    
    organic_filter_w1 = organic_df[(organic_df['Install Time'] >= from_date)&
                                    (organic_df['Install Time'] <= to_date)]
    organic_filter_w2 = organic_df[(organic_df['Install Time'] >= fromdate_lastweek)&
                                    (organic_df['Install Time'] <= todate_lastweek)]
    
    count_w1 = non_organic_filter_w1['Install Time'].count() + organic_filter_w1['Install Time'].count()
    count_w2 = non_organic_filter_w2['Install Time'].count() + organic_filter_w2['Install Time'].count()

    dg = (count_w1 - count_w2)/count_w1

    txt = "{:.0%}".format(dg)
    

    return txt


def pembaca_periods(from_date=None, to_date=None):
    """total Pembaca per periods return text"""

    query = db.session.query(
        db.func.count(gunp.id).label('total_pembaca')
    ).filter(db.func.date(gunp.create_at).between(from_date, to_date)).scalar()

    return query


def guest_register_reader_periods(from_date=None, to_date=None, is_guest=None):
    """guest or register readers per periods text
    0 = registered
    1 = guest 
    """

    query = db.session.query(
        db.func.count(gunp.id).label('total_pembaca')
    ).join(ac, gunp.user_id == ac.id).filter(db.func.date(gunp.create_at).between(from_date, to_date), ac.is_guest == is_guest).scalar()

    return query


def dg_pembaca_periods(from_date=None, to_date=None):
    """daily growth tota; pembaca per periods"""

    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta  

    w1 = pembaca_periods(from_date=from_date, to_date=to_date)
    w2 = pembaca_periods(from_date=fromdate_lastweek, to_date=todate_lastweek)
    
    dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def dg_guest_register_reader(from_date=None, to_date=None, is_guest=None):
    """daily growth guest reader"""

    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta 

    w1 = guest_register_reader_periods(from_date=from_date, to_date=to_date, is_guest=is_guest)
    w2 = guest_register_reader_periods(from_date=fromdate_lastweek, to_date=todate_lastweek, is_guest=is_guest)

    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def user_activity(from_date=None, to_date=None):
    """user activity chart"""

    coin_query = db.session.query(
        db.func.date(gt.created_at).distinct().label('date'),
        db.func.count(gt.id).over(partition_by=db.func.date(gt.created_at)).label('total_pembelian')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)

    register_reader_query = db.session.query(
        db.func.date(gunp.create_at).distinct().label('date'),
        db.func.count(gunp.id).over(partition_by=db.func.date(gunp.create_at)).label('total_registered_pembaca')
    ).join(ac, gunp.user_id == ac.id).filter(db.func.date(gunp.create_at).between(from_date, to_date), ac.is_guest == 0)

    novel_buyer_query = db.session.query(
        db.func.date(gnt.created_at).distinct().label('date'),
        db.func.count(gnt.id).over(partition_by=db.func.date(gnt.created_at)).label('total_pembelian')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date))

    coin_df = pd.DataFrame(coin_query)
    register_reader_df = pd.DataFrame(register_reader_query)
    novel_buyer_df = pd.DataFrame(novel_buyer_query)

    fig = go.Figure(data=[
        go.Bar(x=register_reader_df.date, y=register_reader_df.total_registered_pembaca, name='Registered Reader'),
        go.Bar(x=coin_df.date, y=coin_df.total_pembelian, name='Coin Purchase'),
        go.Bar(x=novel_buyer_df.date, y=novel_buyer_df.total_pembelian, name='Novel Purchase')
    ])

    fig.update_layout(title='User Journey')
    fig.update_xaxes(title='Date', dtick='D1')
    fig.update_yaxes(title='Total Pembelian')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def arpu(from_date=None, to_date=None):
    """average revenue per user"""

    query = db.session.query(
        db.func.avg(gtd.package_price + gtd.package_fee).label('average')
    ).join(gt, gtd.transaction_id == gt.id).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)

    df = pd.DataFrame(query)
    convert_rp = df['average'].apply(lambda x: "Rp. {:,.0f}".format((x)))

    return convert_rp.values[0]


def dg_arpu(from_date=None, to_date=None):
    """daily growth arpu"""
    
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    w1 = db.session.query(
        db.func.avg(gtd.package_price + gtd.package_fee).label('average')
    ).join(gt, gtd.transaction_id == gt.id).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1).scalar()

    w2 = db.session.query(
        db.func.avg(gtd.package_price + gtd.package_fee).label('average')
    ).join(gt, gtd.transaction_id == gt.id).filter(db.func.date(gt.created_at).between(fromdate_lastweek, todate_lastweek), gt.transaction_status == 1).scalar()

    if w1 == 0:
        dg = 0
    else:
        dg = (w1-w2)/w1

    txt = "{:.0%}".format(dg)

    return txt


def cost():
    """overal cost"""

    read_csv = pd.read_csv('cost_revenue.csv', delimiter=',')
    df = pd.DataFrame(read_csv)
    print(df)
    cost_sum = df.cost.sum()
    
    txt = "Rp. {:,.0f}".format(cost_sum)

    return txt


def revenue_cost_chart():
    """revenue to cost chart"""

    read_csv = pd.read_csv('cost_revenue.csv', delimiter=',')
    df = pd.DataFrame(read_csv)
    df['revenue_to_cost'] = pd.to_numeric(df['revenue_to_cost'])

    trace1 = go.Bar(
        x=df['date'],
        y=df['cost'],
        name='Cost',
        yaxis='y'
    )

    trace2 = go.Scatter(
        x=df['date'],
        y=df['revenue_to_cost'],
        name='Cost To Revenue',
        yaxis='y2',
        # Set the y-axis format to be a percentage with 2 decimal places
        hovertemplate='%{y:.2%}'
    )

    trace3 = go.Bar(
        x=df['date'],
        y=df['revenue'],
        name='Revenue',
        yaxis='y'
    )

    # Define the layout with a secondary y-axis
    layout = go.Layout(
        title='Cost To Revenue',
        yaxis=dict(
            title='Cost'
        ),
        yaxis2=dict(
            title='Cost To Revenue',
            overlaying='y',
            side='right',
            # Set the y-axis format to be a percentage with 2 decimal places
            tickformat='.0%'
        )
    )

    # Combine the traces and layout into a Figure object
    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
    ))

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart
