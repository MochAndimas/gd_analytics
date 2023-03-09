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
from apps.dashboard.functions import revenue_days, pembaca_day, pembeli_day, total_gross_revenue
from apps.dashboard.functions import daily_growth_pembaca, daily_growth_pembeli, daily_growth_coin
from apps.dashboard.functions import daily_growth_total_coin, dg_revenue_gross, dg_revenue
from apps.dashboard.functions import coin_days, dg_register, dau_mau_chart
from apps.dashboard.functions import dau_mau_avg_text, pembaca_pembeli_month, beli_coin
from apps.dashboard.functions import revenue_month, transaction_coin_month, af_installs
from apps.dashboard.functions import register, beli_novel, guest_register_reader_periods
from apps.dashboard.functions import dg_af_installs, install_chart, pembaca_periods
from apps.dashboard.functions import dg_pembaca_periods, dg_guest_register_reader, beli_coin_unique, beli_novel_unique
from apps.dashboard.functions import dg_coin_periods, dg_coin_unique_periods, dg_novel_periods, dg_novel_unique_periods
from apps.dashboard.functions import user_activity, arpu, dg_arpu, cost, revenue_cost_chart
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

    # pembaca & pembeli chart /Month
    pmbc_pmbl_month = pembaca_pembeli_month()

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
        pmbc_pmbl_month=pmbc_pmbl_month
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
    dg_revenue_gross_txt = dg_revenue_gross(from_date=to_date, to_date=to_date)
    dg_revenue_txt = dg_revenue()

    # coin purchase /Month
    coin_month = transaction_coin_month()

    # tottal revenue /month chart
    rev_month = revenue_month()

    # total gross revenue chart
    total_gross_rv = total_gross_revenue(from_date='2023-01-01', to_date=to_date)

    # total revenue
    total_rv = total_revenue()

    # total transaksi coin chart
    total_tc = total_transaksi_coin(from_date=from_date, to_date=to_date)

    # category coin chart
    cat_coin = category_coin(from_date=from_date, to_date=to_date)

    # total revenue chart
    rev_days = revenue_days(from_date=from_date, to_date=to_date)

    # pembelian coin /days
    chart_coin_days = coin_days()

    return render_template(
        'coin.html',
        db=db,
        total_gross_rv=total_gross_rv,
        total_rv=total_rv,
        total_tc=total_tc,
        cat_coin=cat_coin,
        rev_days=rev_days,
        dg_coin_expired=dg_coin_expired,
        dg_coin_success=dg_coin_success,
        dg_total_coin=dg_total_coin,
        dg_revenue_gross_txt=dg_revenue_gross_txt,
        dg_revenue_txt=dg_revenue_txt,
        chart_coin_days=chart_coin_days,
        rev_month=rev_month,
        coin_month=coin_month
    )


@blueprint.route('/in-app', methods=['POST','GET'])
@login_required
def in_app_page():
    """in app page"""
    # date to filter
    last2day = datetime.datetime.today() - datetime.timedelta(2)
    las8days = datetime.datetime.today() - datetime.timedelta(8)
    last2day_date = last2day.date()
    last8days_date = las8days.date()
    from_date = last8days_date
    to_date = last2day_date
    delta = (to_date - from_date)+datetime.timedelta(1)
    fromdate_lastweek = from_date - delta
    todate_lastweek = to_date - delta

    if request.method == 'POST':
        from_date = datetime.datetime.strptime(request.form['from'], '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.form['to'], '%Y-%m-%d').date()
    
    """GET methods section"""
    # user aquisition 
    installs_text = af_installs(from_date=from_date, to_date=to_date)
    dau_avg_periods = round(dau_mau_avg_text(from_date=from_date, to_date=to_date, column='daily_active_user'))
    mau_avg_periods = round(dau_mau_avg_text(from_date=from_date, to_date=to_date, column='monthly_active_user'))
    register_week = register(from_date=from_date, to_date=to_date)

    # daily growth user aquisition
    dg_installs = dg_af_installs(from_date=from_date, to_date=to_date)
    dau_avg_w2 = round(dau_mau_avg_text(from_date=fromdate_lastweek, to_date=todate_lastweek, column='daily_active_user'))
    dg_dau = (dau_avg_periods - dau_avg_w2)/dau_avg_w2
    dau_dg = "{:.0%}".format(dg_dau)
    mau_avg_w2 = round(dau_mau_avg_text(from_date=fromdate_lastweek, to_date=todate_lastweek, column='monthly_active_user'))
    dg_mau = (mau_avg_periods - mau_avg_w2)/mau_avg_periods
    mau_dg = "{:.0%}".format(dg_mau)
    daily_growth_register = dg_register(from_date=from_date, to_date=to_date)

    # user aqusition chart
    dau_mau = dau_mau_chart(from_date=from_date, to_date=to_date)
    chart_install = install_chart(from_date=from_date, to_date=to_date)

    # User activity
    pembaca_preiod = pembaca_periods(from_date=from_date, to_date=to_date)
    guest_reader = guest_register_reader_periods(from_date=from_date, to_date=to_date, is_guest=1)
    register_reader = guest_register_reader_periods(from_date=from_date, to_date=to_date, is_guest=0)
    beli_coin_week = beli_coin(from_date=from_date, to_date=to_date).scalar()
    beli_coin_uniques = beli_coin_unique(from_date=from_date, to_date=to_date)
    beli_novel_week = beli_novel(from_date=from_date, to_date=to_date).scalar()
    beli_novel_uniques= beli_novel_unique(from_date=from_date, to_date=to_date)

    # user activity daily growth
    dg_total_pembaca = dg_pembaca_periods(from_date=from_date, to_date=to_date)
    dg_guest_reader = dg_guest_register_reader(from_date=from_date, to_date=to_date, is_guest=1)
    dg_register_reader = dg_guest_register_reader(from_date=from_date, to_date=to_date, is_guest=0)
    dg_coin_period = dg_coin_periods(from_date=from_date, to_date=to_date) # used in cost & revenue too
    dg_coin_unique_period = dg_coin_unique_periods(from_date=from_date, to_date=to_date) 
    dg_novel_period = dg_novel_periods(from_date=from_date, to_date=to_date)
    dg_novel_unique_period = dg_novel_unique_periods(from_date=from_date, to_date=to_date)

    # user activity daily growth
    user_journey_chart = user_activity(from_date=from_date, to_date=to_date)

    # Cost & revenue
    cost_txt = cost()
    revenue = total_gross_revenue(from_date=from_date, to_date=to_date)
    arpu_text = arpu(from_date=from_date, to_date=to_date)

    # daily growth cost &revenue
    dg_revenues = dg_revenue_gross(from_date=from_date, to_date=to_date, timedelta=7)
    dg_arpu_text = dg_arpu(from_date=from_date, to_date=to_date)

    # cost & revenue chart
    revenue_cost_charts = revenue_cost_chart()
    
    return render_template(
        'in_app.html',
        db=db,
        last2day_date=last2day_date,
        last8days_date=last8days_date,
        register_week=register_week,
        beli_coin_week=beli_coin_week,
        beli_novel_week=beli_novel_week,
        beli_coin_uniques=beli_coin_uniques,
        beli_novel_uniques=beli_novel_uniques,
        daily_growth_register=daily_growth_register,
        dau_mau=dau_mau,
        dau_avg_periods=dau_avg_periods,
        mau_avg_periods=mau_avg_periods,
        dau_dg=dau_dg,
        mau_dg=mau_dg,
        installs_text=installs_text, 
        dg_installs=dg_installs,
        chart_install=chart_install,
        pembaca_period=pembaca_preiod,
        guest_reader=guest_reader,
        register_reader=register_reader,
        dg_total_pembaca=dg_total_pembaca,
        dg_guest_reader=dg_guest_reader,
        dg_register_reader=dg_register_reader,
        dg_coin_period=dg_coin_period,
        dg_coin_unique_period=dg_coin_unique_period,
        dg_novel_period=dg_novel_period,
        dg_novel_unique_period=dg_novel_unique_period,
        user_journey_chart=user_journey_chart,
        revenue=revenue,
        dg_revenues=dg_revenues, 
        arpu_text=arpu_text,
        dg_arpu_text=dg_arpu_text,
        cost_txt=cost_txt,
        revenue_cost_charts=revenue_cost_charts)
