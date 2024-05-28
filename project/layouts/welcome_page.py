from dash import html, dcc

def welcome_page():
    return html.Div([
        html.Div([
            html.Div([
                html.H1("Budgetr.", className='welcome-logo'),
                dcc.Link("Sign In", href='/sign_in', className='sign-in-btn'),
                dcc.Link("Create Your Account", href='/sign_up', className='sign-up-btn')    
            ], className= 'welcome-nav')
        ], className= 'welcome-nav-background'),
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Visualize Your Finances", className='welcome-slogan'),
                    html.P("Gain control over your expenses. Discover clear, visual insights into your spending to help you budget smarter and save more.", className='welcome-paragraph'),
                    dcc.Link("Start Today", href='/sign_up', className='sign-up-btn')                          
                ], className='welcome-text'),
                html.Img(src= '/assets/wallet.png', className='welcome-image')
            ], className= "welcome-content")
        ], className='welcome-content-background'),

        html.Div([
            html.Div([
                html.H2("About The Creators"),
                # html.P("After becoming groupmates in "),
                html.Div([
                    html.Div([
                        html.Img(src='assets/masa.png', className='creator-image'),
                        html.H3('Nagamasa (Masa) Kagami'),
                        # html.P('Electrical Engineering Student @ McGill University'),
                        # dcc.Link('LinkedIn', href='your_linkedin_profile', className='social-link'),
                        # html.P('\n'),
                        # dcc.Link('Personal Website', href='masakagami.com', className='social-link')
                    ], className='creator-profile'),
                    html.Div([
                        html.Img(src='/path_to_partner_image.jpg', className='creator-image'),
                        html.H3('Partner Name'),
                        # html.P('A brief bio or description of your partner’s background, expertise, and role in the project.'),
                        # dcc.Link('LinkedIn', href='partner_linkedin_profile', className='social-link')
                    ], className='creator-profile')
                ], className='creators-container')
            ], className='welcome-about')            
        ], className='welcome-about-background')


    ],className='welcome')