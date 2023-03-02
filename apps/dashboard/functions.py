"""functions file dashboard"""

from __future__ import division
import json
import pandas as pd
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


def read_query(text):
    """conevert query statement into pandas"""

    file = pd.read_sql(sql=text, con=db.engine.connect())

    return file


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


def total_gross_revenue():
    """revenue convert lambda"""

    rv = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
    ).join(gt, gt.id == gtd.transaction_id).filter(db.func.date(gt.created_at) >= '2023-01-01', gt.transaction_status == 1)
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


def daily_growth_pembaca_week():
    """daily growth pembaca"""
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    week1 = db.session.query(
        db.func.count(gunp.id).label('today')
    ).filter(db.func.date(gunp.create_at).between(last8days_date, last2day_date)).scalar()
    week2 = db.session.query(
        db.func.count(gunp.id).label('yesterday')
    ).filter(db.func.date(gunp.create_at).between(last15days_date, last9days_date)).scalar()

    if week1 == 0:
        growth = 0
    else:
        growth = (week1-week2)/week1

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


def daily_growth_pembeli_week():
    """daily growth pembeli"""
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    week1 = db.session.query(
        db.func.count(gnt.id).label('today')
    ).filter(db.func.date(gnt.created_at).between(last8days_date, last2day_date)).scalar()
    week2 = db.session.query(
        db.func.count(gnt.id).label('yesterday')
    ).filter(db.func.date(gnt.created_at).between(last15days_date, last9days_date)).scalar()

    if week1 == 0:
        growth = 0
    else:
        growth = (week1-week2)/week1

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

    if today == 0:
        growth = 0
    else:
        growth = (today-yesterday)/today

    txt = "{:.0%}".format(growth)

    return


def daily_growth_coin_week(transaction_status=0):
    """daily growth coin. 0 = Pending, 1 = Success, 2 = Expired"""
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    today = db.session.query(
        db.func.count(gt.id).label('today')
    ).filter(db.func.date(gt.created_at).between(last8days_date, last2day_date), gt.transaction_status == transaction_status).scalar()
    yesterday = db.session.query(
        db.func.count(gt.id).label('yesterday')
    ).filter(db.func.date(gt.created_at).between(last15days_date, last9days_date), gt.transaction_status == transaction_status).scalar()

    if today == 0:
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


def dg_revenue_gross():
    """daily growth gross revenue"""

    today = db.session.query(
        db.func.sum(gtd.package_price+gtd.package_fee).label('revenue')
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


def dg_app_event(event=None):
    """daily growth install"""
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    week1 = db.session.query(
        db.func.sum(event)
    ).filter(aad.date.between(last8days_date, last2day_date)).scalar()
    week2 = db.session.query(
        db.func.sum(event)
    ).filter(aad.date.between(last15days_date, last9days_date)).scalar()

    if week1 == None:
        growth = 0
    else:
        growth = (week1-week2)/week1

    txt = "{:.0%}".format(growth)

    return txt


def dg_register():
    """daily growth register"""
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    week1 = db.session.query(
        db.func.count(ac.id)
    ).filter(db.func.date(ac.registered_at).between(last8days_date, last2day_date), ac.is_guest == 0).scalar()

    week2 = db.session.query(
        db.func.count(ac.id)
    ).filter(db.func.date(ac.registered_at).between(last15days_date, last9days_date), ac.is_guest == 0).scalar()

    if week1 == None:
        growth = 0
    else:
        growth = (week1 - week2)/week1

    txt = "{:.0%}".format(growth)

    return txt


def af(from_date=None, to_date=None):
    """Appsfyer event last week"""
    query_af_w1 = db.session.query(
        db.func.sum(aad.installs).label('installs'),
        db.func.sum(aad.af_preview_novel_counter).label('preview_novel'),
        db.func.sum(aad.af_topup_coin_counter).label('klik_topup_koin')
    ).filter(db.func.date(aad.date).between(from_date, to_date))

    return query_af_w1


def register(from_date=None, to_date=None):
    """total register last week"""
    reg = db.session.query(
        db.func.count(ac.id).label('register')
    ).filter(db.func.date(ac.registered_at).between(from_date, to_date), ac.is_guest == 0)

    return reg


def baca_novel(from_date=None, to_date=None):
    """baca novel last week"""
    baca_novel_w1 = db.session.query(
        db.func.count(gunp.user_id).label('pembaca_novel')
    ).filter(db.func.date(gunp.create_at).between(from_date, to_date))

    return baca_novel_w1


def beli_coin(from_date=None, to_date=None):
    """beli coin last week"""
    beli_coin_w1 = db.session.query(
        db.func.count(gt.user_id).label('beli_coin')
    ).filter(db.func.date(gt.created_at).between(from_date, to_date), gt.transaction_status == 1)

    return beli_coin_w1


def beli_novel(from_date=None, to_date=None):
    """beli_novel last week"""
    beli_novel_w1 = db.session.query(
        db.func.count(gnt.user_id).label('beli_novel')
    ).filter(db.func.date(gnt.created_at).between(from_date, to_date))

    return beli_novel_w1


def in_app_chart():
    """in app chart"""

    last2days = datetime.datetime.today() - datetime.timedelta(2)
    last8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last2days_date = last2days.date()
    last8days_date = last8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()

    df_af_w1 = pd.DataFrame(
        af(from_date=last8days_date, to_date=last2days_date))
    df_af_w2 = pd.DataFrame(
        af(from_date=last15days_date, to_date=last9days_date))
    df_reg_w1 = pd.DataFrame(
        register(from_date=last8days_date, to_date=last2days_date))
    df_reg_w2 = pd.DataFrame(
        register(from_date=last15days_date, to_date=last9days_date))
    df_pembaca_w1 = pd.DataFrame(baca_novel(
        from_date=last8days_date, to_date=last2days_date))
    df_pembaca_w2 = pd.DataFrame(baca_novel(
        from_date=last15days_date, to_date=last9days_date))
    df_coin_w1 = pd.DataFrame(
        beli_coin(from_date=last8days_date, to_date=last2days_date))
    df_coin_w2 = pd.DataFrame(
        beli_coin(from_date=last15days_date, to_date=last9days_date))
    df_pembeli_w1 = pd.DataFrame(beli_novel(
        from_date=last8days_date, to_date=last2days_date))
    df_pembeli_w2 = pd.DataFrame(beli_novel(
        from_date=last15days_date, to_date=last9days_date))

    xaxes_w1 = [df_pembeli_w1.beli_novel.values[0], df_coin_w1.beli_coin.values[0], df_af_w1.klik_topup_koin.values[0],
                df_reg_w1.register.values[0], df_pembaca_w1.pembaca_novel.values[0], df_af_w1.preview_novel.values[0], df_af_w1.installs.values[0]]
    xaxes_w2 = [df_pembeli_w2.beli_novel.values[0], df_coin_w2.beli_coin.values[0], df_af_w2.klik_topup_koin.values[0],
                df_reg_w2.register.values[0], df_pembaca_w2.pembaca_novel.values[0], df_af_w2.preview_novel.values[0], df_af_w2.installs.values[0]]
    yaxes = ['beli_novel', 'beli_coin', 'klik_topup_coin',
             'register', 'pembaca_novel', 'preview_novel', 'installs']

    fig = go.Figure(data=[
        go.Bar(name=f'{last8days_date} - {last2days_date}', y=yaxes, x=xaxes_w1,
               orientation='h', marker=dict(color='red'), text=xaxes_w1, textposition='outside'),
        go.Bar(name=f'{last15days_date} - {last9days_date}', y=yaxes, x=xaxes_w2,
               orientation='h', marker=dict(color='blue'), text=xaxes_w2, textposition='outside')
    ], layout=dict(height=650))

    fig.update_layout(title='App Events /7 Days Periods',
                      barmode='group', legend_title_text="Periods")
    fig.update_xaxes(title='value_counts')
    fig.update_yaxes(title='Events', categoryorder='array', categoryarray=[
        'beli_novel', 'beli_coin', 'klik_topup_coin', 'register', 'pembaca_novel', 'preview_novel', 'installs'
    ])
    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def install_media_source_table(from_date='2023-01-09', to_date='2023-01-30'):
    """install by media source table"""

    query = db.session.query(
        aad.date.label('date'),
        aad.media_source.label('media_source'),
        aad.campaign.label('campaign'),
        aad.installs.label('installs')
    ).filter(db.func.date(aad.date).between(from_date, to_date)).order_by(desc('date'))

    df = pd.DataFrame(query)

    fig = go.Figure(data=[
        go.Table(header=dict(values=df.columns),
                 cells=dict(values=[df.date.values, df.media_source, df.campaign, df.installs]))
    ])
    fig.update_layout(title='Installs By Media Source')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def install_media_source_chart(from_date='2023-01-09', to_date='2023-01-30'):
    """installs by media source chart"""

    query = db.session.query(
        aad.media_source.distinct().label('media_source'),
        db.func.sum(aad.installs).over(
            partition_by=aad.media_source).label('installs')
    ).filter(db.func.date(aad.date).between(from_date, to_date), aad.installs != 0)

    df = pd.DataFrame(query)

    fig = go.Figure(
        go.Bar(x=df.media_source, y=df.installs,
               text=df.installs, textposition='outside')
    )

    fig.update_layout(title='Installs By Media Source')
    fig.update_xaxes(title='Media Source')
    fig.update_yaxes(title='Installs')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def dau_mau_chart(from_date='2023-01-09', to_date='2023-02-23'):
    """DAU & MAU chart"""

    df = pd.read_csv('./dau&mau.csv', delimiter=';')

    filtered_df = df[(df['date'] >= str(from_date))
                     & (df['date'] <= str(to_date))]

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
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Active Users')

    chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart


def dau_mau_sum_text(from_date=None, to_date=None, column=None):
    """DAU & MAU text"""

    df = pd.read_csv('./dau&mau.csv', delimiter=';')

    w1 = df[(df['date'] >= str(from_date)) & (df['date'] <= str(to_date))]

    sums = w1[column].sum()

    return sums


def dau_mau_avg_text(from_date=None, to_date=None, column=None):
    """DAU & MAU text"""

    df = pd.read_csv('./dau&mau.csv', delimiter=';')

    w1 = df[(df['date'] >= str(from_date)) & (df['date'] <= str(to_date))]

    sums = w1[column].mean()

    return sums


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
        go.Bar(x=df_pembeli.periods, y=df_pembeli.pembeli_novel,
               text=df_pembeli.pembeli_novel, textposition='outside', name='pembeli_novel'),
        go.Bar(x=df_pembaca.periods, y=df_pembaca.pembaca_novel,
               text=df_pembaca.pembaca_novel, textposition='outside', name='pembaca_novel')
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
