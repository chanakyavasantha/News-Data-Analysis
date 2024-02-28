from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import pandas as pd
import plotly.express as px
import io
import base64
import matplotlib.pyplot as plt
from plotly import io as pio


df = pd.read_excel('static/all_news.xlsx')
df['Industry sector'] = df['Industry sector'].str.split(', ')
df = df.explode('Industry sector').reset_index(drop=True)
df['News source'] = df['News source'].str.split(', ')
df = df.explode('News source').reset_index(drop=True)
lins = []
for item in df['News source']:
    if item == 'Economic Times' or item == 'The Economic Times' or item == 'Economic Times (ET)' or item =='Economic Times.' or item =='ET (Economic Times)':
        lins.append('Economic Times')
    elif item == 'Not specified' or item == 'Not Mentioned' or item == 'Not mentioned.':
        lins.append('Not Specified')
    elif item == 'Financial news outlet.':
        lins.append('Financial news outlet')
    else:
        lins.append(item)
df['News source'] = lins

df['Target audience'] = df['Target audience'].str.split(', ')
df_expanded = df.explode('Target audience').reset_index(drop=True)
target_audience_distribution = df_expanded['Target audience'].value_counts().reset_index()
target_audience_distribution.columns = ['Target Audience', 'Count']
df['date'] = pd.to_datetime(df['date'], format='mixed')
industry_distribution = df['Industry sector'].value_counts().reset_index()
industry_distribution.columns = ['Industry', 'Count']

# Subsector Distribution
subsector_distribution = df['Subsector'].value_counts().reset_index()
subsector_distribution.columns = ['Subsector', 'Count']


# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)


@on('#intro')
async def page_intro(q: Q):
    q.page['sidebar'].value = '#intro'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='650px'), title='News Analysis',
        image='data:image/png;base64,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',
        content='''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ac sodales felis. Duis orci enim, iaculis at augue vel, mattis imperdiet ligula. Sed a placerat lacus, vitae viverra ante. Duis laoreet purus sit amet orci lacinia, non facilisis ipsum venenatis. Duis bibendum malesuada urna. Praesent vehicula tempor volutpat. In sem augue, blandit a tempus sit amet, tristique vehicula nisl. Duis molestie vel nisl a blandit. Nunc mollis ullamcorper elementum.
Donec in erat augue. Nullam mollis ligula nec massa semper, laoreet pellentesque nulla ullamcorper. In ante ex, tristique et mollis id, facilisis non metus. Aliquam neque eros, semper id finibus eu, pellentesque ac magna. Aliquam convallis eros ut erat mollis, sit amet scelerisque ex pretium. Nulla sodales lacus a tellus molestie blandit. Praesent molestie elit viverra, congue purus vel, cursus sem. Donec malesuada libero ut nulla bibendum, in condimentum massa pretium. Aliquam erat volutpat. Interdum et malesuada fames ac ante ipsum primis in faucibus. Integer vel tincidunt purus, congue suscipit neque. Fusce eget lacus nibh. Sed vestibulum neque id erat accumsan, a faucibus leo malesuada. Curabitur varius ligula a velit aliquet tincidunt. Donec vehicula ligula sit amet nunc tempus, non fermentum odio rhoncus.
Vestibulum condimentum consectetur aliquet. Phasellus mollis at nulla vel blandit. Praesent at ligula nulla. Curabitur enim tellus, congue id tempor at, malesuada sed augue. Nulla in justo in libero condimentum euismod. Integer aliquet, velit id convallis maximus, nisl dui porta velit, et pellentesque ligula lorem non nunc. Sed tincidunt purus non elit ultrices egestas quis eu mauris. Sed molestie vulputate enim, a vehicula nibh pulvinar sit amet. Nullam auctor sapien est, et aliquet dui congue ornare. Donec pulvinar scelerisque justo, nec scelerisque velit maximus eget. Ut ac lectus velit. Pellentesque bibendum ex sit amet cursus commodo. Fusce congue metus at elementum ultricies. Suspendisse non rhoncus risus. In hac habitasse platea dictumst.
        '''
    ))

@on('#data-frame-analysis')
async def page_df(q: Q):
    q.page['sidebar'].value = '#data-frame-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)
    table_rows = []
    for index, row in df.iterrows():
        table_rows.append(ui.table_row(
            name=row['title'],
            cells=[row['title'], row['News source'],]  # Adjust these indices based on your CSV columns
        ))
    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='Title', label='Title', searchable=True,min_width='500'),
            ui.table_column(name='News Source', label='News Source', filterable=True, min_width='1000',cell_type=ui.tag_table_cell_type(name='tags', tags=[
                    ui.tag(label='RUNNING', color='#D2E3F8'),
                    ui.tag(label='DONE', color='$red'),
                    ui.tag(label='SUCCESS', color='$mint'),
                    ]
                ))
        ],
        events = ['click'],
        rows=table_rows)
    ]))

@on('table')
async def handle_table_click(q: Q):
    table_rows = []
    for index, row in df.iterrows():
        table_rows.append(ui.table_row(
            name=row['title'],
            cells=[row['title'], row['News source'],]  # Adjust these indices based on your CSV columns
        ))
    print(q.args.table)
    if q.args.table:
        q.client.selected_actor = q.args.table[0]
        q.args['#'] = 'data-frame-analysis'
        await page_df(q)

@on('#column-analysis')
async def pageca(q: Q):
    print('Handling page4')

    q.page['sidebar'].value = '#column-analysis'
    clear_cards(q)

    column_names = df.columns.tolist()

    if q.args.plot_button:
        print('Plot button clicked')
        selected_column = q.args.selected_column
        print(f'Plotting graph for {selected_column}')

        plot_fig = plot_categorical_graph(df, selected_column)

        # Add a card to display the plot
        config = {
            'scrollZoom': False,
            'showLink': False,
            'displayModeBar': False
        }
        html = pio.to_html(plot_fig, validate=False, include_plotlyjs='cdn', config=config)
        add_card(q, 'col1', ui.form_card(box=ui.box('zone1'), title='', items=[
            ui.frame(content=html, height='1000px', width='1500px')]))

    else:
        print('Rendering dropdown menu')
        # Add a dropdown to select a column
        dropdown_card = ui.form_card(box=ui.box('horizontal'), items=[
            ui.dropdown(name='selected_column', label='Select Column', choices=[ui.choice(name=col, label=col) for col in column_names]),
            ui.button(name='plot_button', label='Submit', primary=True),
        ])
        add_card(q, 'dropdown_card', dropdown_card)

@on('#industry-sector-sentiment-analysis')
async def page_ind(q: Q):
    q.page['sidebar'].value = '#industry-sector-sentiment-analysis'
    clear_cards(q)  # When routting, drop all the cards except of the main ones (header, sidebar, meta).
    '''
    add_card( q, 'dataframe', ui.form_card(box='zone2', items=[
        # modify heading here (content)
        ui.text_xl(content='Data Frame Head'),
        ui.table(
            name='table',
            columns=[ui.table_column(name=i, label=i, min_width='200',cell_type=ui.markdown_table_cell_type(target='_blank')) for i in df.columns],
            height='400px',
            rows=[ui.table_row(name=f'row{i}', cells=list(str(i) for i in df.values[i])) for i in range(100)],
        )
    ]))
    '''
    # Identify the top 10 industry sectors with positive sentiment
    # Assuming you have a 'Sentiment' column in your DataFrame
    positive_rows = df[df['Sentiment'].str.lower().str.contains('positive')]
    

    # Extract the top 10 industry sectors with positive sentiment
    
    # Assuming you already have 'positive_rows' DataFrame
    # Extract the top 10 industry sectors with positive sentiment
    positive_industries = positive_rows['Industry sector'].value_counts().head(10)
    positive_industries = positive_industries[1:]

    # Create a pie chart using plotly express
    fig = px.pie(positive_industries, 
             names=positive_industries.index, 
             values=positive_industries.values, 
             title='Top 10 Industry Sectors with Positive Sentiment')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'piechart1', ui.frame_card(box='horizontal', title='', content=html))
    # Identify the top 10 industry sectors with negative sentiment
    # Assuming you have a 'Sentiment' column in your DataFrame
    negative_rows = df[df['Sentiment'].str.lower().str.contains('negative')]
    # Extract the top 10 industry sectors with negative sentiment
    negative_industries = negative_rows['Industry sector'].value_counts().head(10)
    add_card(q, 'dataframe3', ui.form_card(box='horizontal', items=[
        ui.text_xl(content='Top 10 Industry Sectors with Most Negative Sentiment'),
        ui.table(
            name='negative_table',
            columns=[
                ui.table_column(name='Industry Sector', label='Industry Sector', min_width='200'),
                ui.table_column(name='Count', label='Negative Sentimental NewsCount', min_width='200')
            ],
            rows=[ui.table_row(name = f'count{count}',cells=[sector , str(count)]) for sector, count in negative_industries.items() if sector != '0'],
            height='400px',
        )
    ]))
    positive_news_source = positive_rows['News source'].value_counts().head(13)
    del positive_news_source['0']
    del positive_news_source['Not mentioned']
    del positive_news_source['Not specified.']
    fig = px.pie(positive_news_source,
                 names = positive_news_source.index,
                 values = positive_news_source.values,
                 title = 'Top 10 Positive News Sources')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'piechart2', ui.frame_card(box='zone1', title='', content=html))
    

    negative_news_source = negative_rows['News source'].value_counts().head(10)
    add_card(q, 'datafram2', ui.form_card(box='zone1', items=[
        ui.text_xl(content='Top 10 Negative News Sources'),
        ui.table(
            name='negative_table_News_source',
            columns=[
                ui.table_column(name='Industry Sector', label='Industry Sector', min_width='200'),
                ui.table_column(name='Count', label='Negative Sentimental NewsCount', min_width='200')
            ],
            rows=[ui.table_row(name = f'count{count}',cells=[sector , str(count)]) for sector, count in negative_news_source.items() if sector != '0'],
            height='400px'
        )
    ]))
    


@on('#temporal-analysis')
async def page_temporal(q: Q):
    q.page['sidebar'].value = '#temporal-analysis'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    
    # Create a histogram using Plotly for temporal distribution
    fig_temporal = px.histogram(df, x='date', nbins=30, labels={'date': 'Date', 'count': 'Number of Articles'})
    fig_temporal.update_layout(title='Temporal Distribution of Articles', xaxis_title='Date', yaxis_title='Number of Articles')
    config_temporal = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html_temporal = pio.to_html(fig_temporal, validate=False, include_plotlyjs='cdn', config=config_temporal)
    add_card(q, 'temporal1', ui.form_card(box=ui.box('horizontal', width='750px'), title='', items=[
        ui.frame(content=html_temporal, height='650px', width='650px')]))

    # Create a grouped bar chart for industry representation
    fig_industry = px.histogram(df, x='date', color='Industry sector', nbins=30,
                                 labels={'date': 'Date', 'count': 'Number of Articles', 'Industry sector': 'Industry'})
    fig_industry.update_layout(title='Industry Representation Over Time', xaxis_title='Date', yaxis_title='Number of Articles')
    config_industry = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html_industry = pio.to_html(fig_industry, validate=False, include_plotlyjs='cdn', config=config_industry)
    add_card(q, 'industry1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html_industry, height='650px', width='1500px')]))

    


    

    






@on('#ind-sub-analysis')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#ind-sub-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # Now df_expanded has each industry on a separate row

    

    # Plot Industry Distribution
    fig_industry = px.bar(industry_distribution, x='Industry', y='Count', title='Distribution of News Across Industries')
    fig_industry.update_layout(xaxis_title='Industry', yaxis_title='Number of Articles')
    fig_industry.update_traces(width=2)
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig_industry, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'ind1', ui.form_card(box=ui.box('horizontal',width='1500px'), title='', items=[
        ui.frame(content=html, height='1000px',width='1500px')]))

@on('#target-audience-analysis')
async def page_target_aud(q: Q):
    q.page['sidebar'].value = '#target-audience-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    


    # Plot Target Audience Distribution
    fig_target_audience = px.bar(target_audience_distribution, x='Target Audience', y='Count', title='Target Audience Analysis')

    # Increase bar width if needed
    fig_target_audience.update_layout(yaxis_range=[0, 100])
    fig_target_audience.update_traces(width=3)


    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig_target_audience, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'aud1', ui.form_card(box=ui.box('horizontal',width='1500px'), title='', items=[
        ui.frame(content=html, height='1000px',width='1500px')]))

    

@on('#competitor-analysis')
async def page_comp(q: Q):
    q.page['sidebar'].value = '#competitor-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

@on('#salary-analysis')
async def page_salary(q: Q):
    q.page['sidebar'].value = '#salary-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

@on('#cross-industry-analysis')
async def page_cross(q: Q):
    q.page['sidebar'].value = '#cross-industry-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

def plot_categorical_graph(df, selected_column):
    # Assuming data is present in a column named 'data'
    fig = px.histogram(df, x=selected_column, title=f'Distribution of {selected_column}')
    return fig




    




@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]


@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='300px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', direction=ui.ZoneDirection.ROW,),
                    ui.zone('zone2',direction=ui.ZoneDirection.ROW ),
                    ui.zone('vertical'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
                    ui.zone(name='zone1', direction=ui.ZoneDirection.ROW),
                    ui.zone(name='zone3',direction=ui.ZoneDirection.COLUMN)
                ]),
            ]),
        ])
    ])])
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title = 'News Data Analyzer', subtitle="by Harsha Vardhan",
        value=f'#{q.args["#"]}' if q.args['#'] else '#intro',
        image='', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#intro', label='Home'),
                ui.nav_item(name='#data-frame-analysis', label='Data Frame Analysis'),
                ui.nav_item(name='#column-analysis', label='Column Analysis'),
                ui.nav_item(name='#industry-sector-sentiment-analysis', label='Industry Sector Sentiment Analysis'),
                ui.nav_item(name='#ind-sub-analysis', label='Industry and sub sector comparision'),
                ui.nav_item(name='#temporal-analysis', label='Temporal Analysis'),
                ui.nav_item(name='#target-audience-analysis', label='Target Audience Analysis'),
                ui.nav_item(name='#competitor-analysis', label='Competitor Analysis'),
                ui.nav_item(name='#salary-analysis',label='Salary Analysis'),
                ui.nav_item(name='#cross-industry-analysis',label='Cross Industry Analysis'),
                
            ]),
        ],
        secondary_items=[
            ui.persona(title='Harsha Vardhan', subtitle='Data Scientist , Developer, Researcher in AI', size='s',
                       image=''),
        ]
    )
    q.page['header'] = ui.header_card(
        box='header', title='', subtitle='',
        items=[
            ui.persona(title='Harsha', subtitle='Developer', size='xs',
                       image=''),
        ]
    )

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page_intro(q)


@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)
    await q.page.save()
