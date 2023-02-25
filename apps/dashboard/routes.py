"""dashboard routes file"""

import pandas as pd
import datetime
from flask import render_template, request
from flask_login import login_required
from datetime import date

from apps import db, csrf
from apps.dashboard import blueprint
from apps.authentication.models import AppsflyerAggregatedData as aad
from apps.dashboard.functions import pembaca_pgnt, pembeli_pgnt, total_pembaca_month
from apps.dashboard.functions import total_pembeli_month, genre_pembeli, genre_pembaca
from apps.dashboard.functions import total_revenue, total_transaksi_coin, category_coin
from apps.dashboard.functions import revenue_month, pembaca_day, pembeli_day, total_gross_revenue
from apps.dashboard.functions import daily_growth_pembaca, daily_growth_pembeli, daily_growth_coin
from apps.dashboard.functions import daily_growth_total_coin, dg_revenue_gross, dg_revenue
from apps.dashboard.functions import coin_days, dg_app_event, in_app_chart
from apps.dashboard.functions import install_media_source_table, install_media_source_chart, dau_mau_chart
from apps.dashboard.functions import dau_mau_sum_text, dau_mau_avg_text
from decouple import config


DEBUG = config('DEBUG', default=True, cast=bool)


@blueprint.route('/', methods=['POST', 'GET'])
@blueprint.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard_page():
    """dashboard page"""

    # Date to filter
    last_30_days = datetime.datetime.today() - datetime.timedelta(30)
    from_date = last_30_days.date()
    to_date = date.today()
    last_1_days = datetime.datetime.today() - datetime.timedelta(1)
    yesterday_date = last_1_days.date()

    if request.method == 'POST':
        from_date = request.form['from']
        to_date = request.form['to']

    """GET Methods Section"""
    # persentase daily growth pembaca
    dg_pembaca = daily_growth_pembaca(from_date=yesterday_date, to_date=date.today())
    dg_pembeli = daily_growth_pembeli(from_date=yesterday_date, to_date=date.today())

    # pembaca stack chart & pembeli bar chart
    stack_chart = total_pembaca_month(from_date, to_date)
    bar_chart = total_pembeli_month(from_date, to_date)

    # pembaca & pembeli per day chart
    pmbc_per_day = pembaca_day(from_date, to_date)
    pmbl_per_day = pembeli_day(from_date, to_date)

    # chart genre
    genre_pembeli_chart = genre_pembeli(from_date, to_date)
    genre_pembaca_chart = genre_pembaca(from_date, to_date)

    # Table pembaca dan pembeli
    pembaca_paginate = pembaca_pgnt(from_date, to_date)
    pembeli_paginate = pembeli_pgnt(from_date, to_date)

    return render_template(
        './dashboard.html',
        db=db,
        csrf=csrf,
        pembaca_paginate=pembaca_paginate,
        pembeli_paginate=pembeli_paginate,
        stack_chart=stack_chart,
        bar_chart=bar_chart,
        genre1_chart=genre_pembeli_chart,
        genre2_chart=genre_pembaca_chart,
        pmbc_per_day=pmbc_per_day,
        pmbl_per_day=pmbl_per_day,
        dg_pembaca=dg_pembaca,
        dg_pembeli=dg_pembeli,
    )


@blueprint.route('/coin', methods=['POST', 'GET'])
@login_required
def coin_page():
    """tbales page"""

    # dates for filter
    last_30_days = datetime.datetime.today() - datetime.timedelta(30)
    from_date = last_30_days.date()
    to_date = date.today()
    last_1_days = datetime.datetime.today() - datetime.timedelta(1)
    yesterday_date = last_1_days.date()

    if request.method == 'POST':
        from_date = request.form['from']
        to_date = request.form['to']

    """GET METHODS section"""
    # daily growth
    dg_coin_expired = daily_growth_coin(transaction_status=2,from_date=yesterday_date, to_date=date.today())
    dg_coin_success = daily_growth_coin(transaction_status=1, from_date=yesterday_date, to_date=date.today())
    dg_total_coin = daily_growth_total_coin()
    dg_revenue_gross_txt = dg_revenue_gross()
    dg_revenue_txt = dg_revenue()

    # total gross revenue chart
    total_gross_rv = total_gross_revenue()

    # total revenue
    total_rv = total_revenue()

    # total transaksi coin chart
    total_tc = total_transaksi_coin(from_date=from_date, to_date=to_date)

    # category coin chart
    cat_coin = category_coin(from_date=from_date, to_date=to_date)

    # total revenue chart
    rev_month = revenue_month(from_date=from_date, to_date=to_date)

    # pembelian coin /days
    chart_coin_days = coin_days()

    return render_template(
        'coin.html',
        db=db,
        total_gross_rv=total_gross_rv,
        total_rv=total_rv,
        total_tc=total_tc,
        cat_coin=cat_coin,
        rev_month=rev_month,
        dg_coin_expired=dg_coin_expired,
        dg_coin_success=dg_coin_success,
        dg_total_coin=dg_total_coin,
        dg_revenue_gross_txt=dg_revenue_gross_txt,
        dg_revenue_txt=dg_revenue_txt,
        chart_coin_days=chart_coin_days
    )


@blueprint.route('/in-app', methods=['POST','GET'])
@login_required
def in_app_page():
    """in app page"""
    # date to filter
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    last3day = datetime.datetime.today() - datetime.timedelta(3)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last9days = datetime.datetime.today() - datetime.timedelta(9)
    last15days = datetime.datetime.today() - datetime.timedelta(15)
    last_30_days = datetime.datetime.today() - datetime.timedelta(30)
    last2day_date = last2day.date()
    last3day_date = last3day.date()
    last8days_date = las8days.date()
    last9days_date = last9days.date()
    last15days_date = last15days.date()
    from_date = last_30_days.date()
    to_date = date.today()

    if request.method == 'POST':
        from_date = request.form['from']
        to_date = request.form['to']

    """GET methods section"""
    # daily growth
    daily_growth_install = dg_app_event(event=aad.installs)
    daily_growth_preview_novel = dg_app_event(
        event=aad.af_preview_novel_counter)
    daily_growth_baca_novel = daily_growth_pembaca(from_date=last3day_date, to_date=last2day_date)
    daily_growth_register = dg_app_event(event=aad.af_register_unique)
    daily_growth_topup_coin = dg_app_event(event=aad.af_topup_coin_unique)
    daily_growth_beli_coin = daily_growth_coin(transaction_status=1, from_date=last3day_date, to_date=last2day_date)
    daily_growth_pembeli_novel = daily_growth_pembeli(from_date=last3day_date, to_date=last2day_date)

    # inapp chart
    inapp_chart = in_app_chart()

    # installs by media source table
    table = install_media_source_table(from_date=from_date, to_date=to_date)
    chart = install_media_source_chart(from_date=from_date, to_date=to_date)
    
    # DAU & MAU chart
    dau_mau = dau_mau_chart(from_date=from_date, to_date=to_date)
    dau_sum = dau_mau_sum_text(from_date=last8days_date, to_date=last2day_date, column='daily_active_user')
    mau_sum = dau_mau_sum_text(from_date=last8days_date, to_date=last2day_date, column='monthly_active_user')
    dau_avg = round(dau_mau_avg_text(from_date='2023-01-09', to_date=to_date, column='daily_active_user'),1)
    mau_avg = round(dau_mau_avg_text(from_date='2023-01-09', to_date=to_date, column='monthly_active_user'),1)

    # daily growth DAU & MAU
    dau_sum_w2 = dau_mau_sum_text(from_date=last15days_date, to_date=last9days_date, column='daily_active_user')
    dg_dau = (dau_sum - dau_sum_w2)/dau_sum
    dau_dg = "{:.0%}".format(dg_dau)
    mau_sum_w2 = dau_mau_sum_text(from_date=last15days_date, to_date=last9days_date, column='monthly_active_user')
    dg_mau = (mau_sum - mau_sum_w2)/mau_sum
    mau_dg = "{:.0%}".format(dg_mau)
    
    return render_template(
        'in_app.html',
        db=db,
        daily_growth_install=daily_growth_install,
        daily_growth_preview_novel=daily_growth_preview_novel,
        daily_growth_baca_novel=daily_growth_baca_novel,
        daily_growth_register=daily_growth_register,
        daily_growth_topup_coin=daily_growth_topup_coin,
        daily_growth_beli_coin=daily_growth_beli_coin,
        daily_growth_pembeli_novel=daily_growth_pembeli_novel,
        inapp_chart=inapp_chart,
        table=table,
        chart=chart,
        dau_mau=dau_mau,
        dau_sum=dau_sum,
        mau_sum=mau_sum,
        dau_avg=dau_avg,
        mau_avg=mau_avg,
        dau_dg=dau_dg,
        mau_dg=mau_dg)
