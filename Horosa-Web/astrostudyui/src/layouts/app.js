import React from 'react';
import { connect  } from 'dva';
import { Layout,  BackTop, Spin,  } from 'antd';
import * as AstroConst from '../constants/AstroConst';
import PageHeader from '../components/homepage/PageHeader';
import styles from './app.less';

const App = ({children, dispatch, app, user, })=>{
    const { userInfo, charts, admin, } = user;
    const { chartDisplay, colorTheme,} = app;
    const { Header, Content } = Layout;

    function menuClick({item, key, keyPath}){
        dispatch({
            type: 'app/menuClick',
            payload: {
                item: item,
                key: key,
                keyPath: keyPath,
            },
        });
    }

    AstroConst.setColorTheme(colorTheme);

    let mainstyle = {
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        background: AstroConst.AstroColor.Background,
        color: AstroConst.AstroColor.TextStroke,
        stroke: AstroConst.AstroColor.TextStroke,
    };
    let headerstyle = {
        position: 'fixed', width:'100%', zIndex: 100, 
        backgroundColor: AstroConst.AstroColor.Backgroud, 
        height:64, padding: 0,
        borderBottom: '2px solid', 
        borderBottomColor: '#e8e8e8',
        color: AstroConst.AstroColor.TextStroke,
        stroke: AstroConst.AstroColor.TextStroke,
    };
    let contentStyle = {
        marginTop: 64,
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
        boxSizing: 'border-box',
        backgroundColor: AstroConst.AstroColor.Backgroud, 
        color: AstroConst.AstroColor.TextStroke,
        stroke: AstroConst.AstroColor.TextStroke,
    };

    return (
        <Layout style={mainstyle}>
            <Header style={headerstyle}>
                <PageHeader 
                    admin={admin}
                    chartDisplay={chartDisplay}
                    colorTheme={colorTheme}
                    userInfo={userInfo} 
                    onMenuClick={menuClick}
                    dispatch={dispatch}
                />
            </Header>

            <Content id='mainContent' style={contentStyle}>
                <div style={{ width:'100%', height: '100%', paddingLeft: 30, paddingRight:30, overflow: 'hidden' }}>
                    <BackTop visibilityHeight={50}/>
                    <div style={{height: '100%', paddingLeft: 30, paddingRight:30, paddingTop:30, overflow: 'hidden'}}>
                        {children}
                    </div>
                </div>
            </Content>

            <div id='globalFooter' style={{height: 0, overflow: 'hidden'}} />
        </Layout>
    );
};


function mapStateToProps(state){
    const { app, user, router } = state;
    const { location } = router;
    const { query } = location;

    return {
        app: app,
        user: user,
        query: query,
    };
}


export default connect(mapStateToProps)(App);
