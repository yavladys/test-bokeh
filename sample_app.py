
from bokeh.io import curdoc
from bokeh.models import (ColorBar, GeoJSONDataSource, HoverTool, LinearColorMapper, DateSlider, LabelSet, Select,
                          Panel, Tabs)
from bokeh.layouts import column, row
from bokeh.palettes import brewer
from bokeh.plotting import figure
import geopandas as gpd
import pandas as pd
from datetime import date, datetime
from datetime import timedelta

# Import geopandas package
# Read in shapefile and examine data
contiguous_ukr = gpd.read_file('data/ukr_admbnda_adm1_q2_sspe_20171221.shp',
                              encoding='utf-8')

contiguous_ukr.loc[contiguous_ukr['ADM1_PCODE']=='UA80', 'ADM1_UA']='м.Київ'
contiguous_ukr['centr_x'] = contiguous_ukr['geometry'].apply(lambda point: point.centroid.x)
contiguous_ukr['centr_y'] = contiguous_ukr['geometry'].apply(lambda point: point.centroid.y)

to_append1 = contiguous_ukr[contiguous_ukr['ADM1_UA']!='м.Київ']
to_append2 = contiguous_ukr[contiguous_ukr['ADM1_UA']=='м.Київ']
contiguous_ukr = pd.concat([to_append1, to_append2])

orig_df = pd.read_csv("data/data.csv")
data = orig_df.copy()
data.index = pd.to_datetime(data['Дата'], format="%d.%m.%Y %H:%M:%S").dt.date
data.index.name = 'Date'


FEATURES_DOC = [
    'Всі лікарі, які можуть бути задіяні з COVID-19 (усі спеціальності)', 'Лікарі, які вже працюють з пацієнтами з COVID-19',
    'Лікарів у денній зміні', 'Лікарів у нічній зміні', 'Всі медсестри', 'Медсестри, які вже працюють з пацієнтами з COVID-19',
    'Медсестер у денній зміні', 'Медсестер у нічній зміні', 'Всього молодшого медичного персоналу',
    'Молодшого медперсоналу, який вже працюють з пацієнтами з COVID-19', 'Молодшого медперсоналу у денній зміні',
    'Молодшого медперсоналу у нічній зміні'
]
FEATURES_BED = [
    'Ліжок загалом','Інфекційних', 'Зайнято інфекційних', 'Реанімаційні / Інтенсивної терапії','Зайнято реанімаційні / інтенсивної терапії',
    'Зайнято загалом ліжок', 'Для пере-профілювання','Зайнято хворими з COVID-19'
]
FEATURES_EQUIP = [
    'Справних ШВЛ високого класу', 'ШВЛ високого класу підключено до пацієнтів', 'Справних ШВЛ середнього класу',
    'ШВЛ середнього класу підключено до пацієнтів', 'Справних ШВЛ дитячих (0-6 років)', 'Пацієнтів підключених до ШВЛ дитячих',
    'Справних портативних (транспортних) ШВЛ', 'Несправних ШВЛ (усіх видів)', 'Моніторів пацієнта поліфункціональних',
    'Екстракорпоральних оксигенаторів (ЕКМО)', 'Екстракорпоральних оксигенаторів (ЕКМО) у використанні ( підключено до пацієнтів)',
    'Апарат  «Штучна нирка» - є чи немає', 'Кількість кисневих концентраторів', 'Газоаналізатор крові - є чи немає',
    'Халати ізоляційні одноразові залишок', 'Халати ізоляційні одноразові використано за добу',
    'Респіратори класу захисту не менше FFP2 (FFP2, FFP3, N-95) залишок',
    'Респіратори класу захисту не менше FFP2 (FFP2, FFP3, N-95) витрати на добу',
    'Костюми біозахисту одноразові залишок', 'Костюми біозахисту одноразові залишок витрати на добу',
    'Маски медичні (хірургічні) одноразові залишок','Маски медичні (хірургічні) одноразові  витрати на добу',
    'Маски медичні багаторазові залишок', 'Маски медичні багаторазові витрати на добу',
    'Захист очей  (захисні щитки та окуляри) одноразові залишок',
    'Захист очей  (захисні щитки та окуляри) одноразові витрати на добу',
    'Захист очей  (захисні щитки та окуляри) багаторазові залишок',
    'Захист очей  (захисні щитки та окуляри) багаторазові витрати на добу',
    'Рукавички нітрилові нетальковані (нестерильні) залишок', 'Рукавички нітрилові нетальковані оглядові (нестерильні) витрати на добу',
    'Спиртовмісний антисептик залишок', 'Спиртовмісний антисептик витрати на добу','швидких тестів залишок',
    'швидких тестів використано за добу', 'ПЦР залишок', 'ПЦР використано',
    'Кількість тампонів та стерильних пробірок з транспортним середовищем залишок',
    'Кількість тампонів та стерильних пробірок з транспортним середовищем використано за добу',
    'З них анестезіологів', 'З них інфекціоністів', 'Боксовані палати', 'Зайнято боксованих', 'Кількість кисневих генераторів до ШВЛ',
    'Рентген апарат', 'Наявність системи централізованого постачання кисню'
]


select_feature = Select(title='Обрати характеристику', value=FEATURES_DOC[0], options=FEATURES_DOC)
slider_time = DateSlider(title='Select day:', start=date(2020, 3, 31), end=datetime.now().date() - timedelta(days=1),
                         value=datetime.now().date() - timedelta(days=1), step=10)


def create_sample(day):
    grouped_df = data[data.index == day].groupby('Область')[FEATURES_BED + FEATURES_EQUIP + FEATURES_DOC].agg(
        sum).reset_index()
    grouped_merged_df = contiguous_ukr.merge(grouped_df, how='left', left_on='ADM1_UA', right_on='Область')
    return grouped_merged_df


def get_max_feature_value_on_day(feature, day):
    return create_sample(day)[feature].max()


def ts_to_day(ts):
    return datetime.fromtimestamp(ts / 1000.0).date()


def make_tick_labels(n, buckets=5):
    return {str(i * (n // buckets)): str(i * (n // buckets)) for i in range(buckets + 1)}


palette = brewer['Oranges'][9]
palette = palette[::-1]
color_mapper = LinearColorMapper(palette=palette, low=0,
                                 high=get_max_feature_value_on_day(select_feature.value,
                                                                   slider_time.value_as_date))

geosource = GeoJSONDataSource(geojson=create_sample(slider_time.value_as_date).to_json())


def make_plot():
    p = figure(title='Map of Ukraine', plot_height=700, plot_width=1000)
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.patches('xs', 'ys', source=geosource,
              fill_color={'field': FEATURES_DOC[0],
                          'transform': color_mapper},
              line_color='gray',
              line_width=0.8,
              hover_fill_color='lightgrey',
              hover_line_color='black',
              fill_alpha=1,
              hatch_color="firebrick", hatch_alpha=10.5,
              name='map')
    return p


plot = make_plot()

tab_doc = Panel(child=column(row(select_feature), row(slider_time), row(plot)), title="Лікарі")
tab_bed = Panel(child=column(row(select_feature), row(slider_time), row(plot)), title="Ліжка")
tab_equip = Panel(child=column(row(select_feature), row(slider_time), row(plot)), title="Обладнання")
tabs = Tabs(tabs=[tab_doc, tab_bed, tab_equip])

label_figures = LabelSet(x='centr_x', y='centr_y', text=select_feature.value, x_offset=5, y_offset=-10,
                         source=geosource, render_mode='canvas', text_font_size='12px', text_align='left')
plot.add_layout(label_figures)

color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=8,
                     width=500, height=20,
                     border_line_color=None,
                     location=(0, 0),
                     orientation='horizontal',
                     major_label_overrides=
                     make_tick_labels(n=get_max_feature_value_on_day(select_feature.value,
                                                                     slider_time.value_as_date)))
plot.add_layout(color_bar, 'above')

labels = LabelSet(x='centr_x', y='centr_y', text='ADM1_UA',
                  x_offset=5, y_offset=5, source=geosource, render_mode='canvas', text_font_size='8px',
                  text_align='left')
plot.add_layout(labels)


def update_legend_color_bar(feature, day):
    new_max_color_value = get_max_feature_value_on_day(feature, day)
    tick_labels = make_tick_labels(new_max_color_value)
    color_bar.major_label_overrides = tick_labels


def update_color_mapper(feature, day):
    color_mapper.high = get_max_feature_value_on_day(feature, day)
    plot.select(name='map').glyph.fill_color = {'field': feature, 'transform': color_mapper}


def update_tooltips_after_feature_change(attr, old, new):
    TOOLTIPS = [(new, '@{' + str(new) + '}')]
    plot.tools = [tool for tool in plot.tools if type(tool) != HoverTool]
    hover = HoverTool(tooltips=TOOLTIPS)
    plot.add_tools(hover)


def update_tabs(attr, old, new):
    if (new == 0):
        select_feature.options = FEATURES_DOC
        select_feature.value = FEATURES_DOC[0]
    elif (new == 1):
        select_feature.options = FEATURES_BED
        select_feature.value = FEATURES_BED[0]
    else:
        select_feature.options = FEATURES_EQUIP
        select_feature.value = FEATURES_EQUIP[0]


def update_color_mapper_and_legend_color_bar_after_feature_change(attr, old, new):
    day = slider_time.value_as_date
    update_color_mapper(new, day)
    update_legend_color_bar(new, day)


def update_color_mapper_and_legend_color_bar_after_day_change(attr, old, new):
    day = ts_to_day(new)
    update_color_mapper(select_feature.value, day)
    update_legend_color_bar(select_feature.value, day)


def update_src_after_day_change(attr, old, new):
    day = ts_to_day(new)
    geosource.geojson = create_sample(day).to_json()


def update_label_figures_after_feature_change(attr, old, new):
    label_figures.text = new


TOOLTIPS = [(select_feature.value, '@{' + str(select_feature.value) + '}')]
plot.add_tools(HoverTool(tooltips=TOOLTIPS))

tabs.on_change('active', update_tabs)

select_feature.on_change('value', update_color_mapper_and_legend_color_bar_after_feature_change)
select_feature.on_change('value', update_tooltips_after_feature_change)
select_feature.on_change('value', update_label_figures_after_feature_change)

slider_time.on_change('value_throttled', update_src_after_day_change)
slider_time.on_change('value_throttled', update_color_mapper_and_legend_color_bar_after_day_change)


curdoc().add_root(column(tabs))