import React from 'react';
import { connect  } from 'dva';
import { Layout,  BackTop,  } from 'antd';
import * as AstroConst from '../constants/AstroConst';
import PageHeader from '../components/homepage/PageHeader';
import {
    APPEARANCE_DARK,
    applyAppearanceToDocument,
    resolveAppearance,
} from '../utils/appearance';
import styles from './app.less';

const App = ({children, dispatch, app, user, })=>{
    const { userInfo, admin, } = user;
    const { chartDisplay, appearanceMode,} = app;
    const { Header, Content } = Layout;
    const [prefersDark, setPrefersDark] = React.useState(()=>{
        if(typeof window === 'undefined' || !window.matchMedia){
            return false;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    });
    const resolvedAppearance = resolveAppearance(appearanceMode, prefersDark);

    React.useEffect(()=>{
        if(typeof window === 'undefined' || !window.matchMedia){
            return;
        }
        const media = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (evt)=>{
            setPrefersDark(!!evt.matches);
        };
        if(media.addEventListener){
            media.addEventListener('change', handleChange);
        }else if(media.addListener){
            media.addListener(handleChange);
        }
        setPrefersDark(!!media.matches);
        return ()=>{
            if(media.removeEventListener){
                media.removeEventListener('change', handleChange);
            }else if(media.removeListener){
                media.removeListener(handleChange);
            }
        };
    }, []);

    React.useEffect(()=>{
        applyAppearanceToDocument(appearanceMode, resolvedAppearance);
        if(dispatch){
            dispatch({
                type: 'app/save',
                payload: {
                    resolvedAppearance: resolvedAppearance,
                },
            });
        }
    }, [appearanceMode, resolvedAppearance]);

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

    AstroConst.setColorTheme(resolvedAppearance === APPEARANCE_DARK ? 8 : AstroConst.DefaultColorTheme);

    let mainstyle = {
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        background: 'var(--horosa-bg)',
        color: 'var(--horosa-text)',
        stroke: 'var(--horosa-text)',
    };
    let headerstyle = {
        position: 'fixed', width:'100%', zIndex: 100,
        backgroundColor: 'var(--horosa-header-bg)',
        height:72, padding: 0,
        borderBottom: '1px solid',
        borderBottomColor: 'var(--horosa-border)',
        color: 'var(--horosa-text)',
        stroke: 'var(--horosa-text)',
    };
    let contentStyle = {
        marginTop: 72,
        height: 'calc(100vh - 72px)',
        overflow: 'hidden',
        boxSizing: 'border-box',
        backgroundColor: 'var(--horosa-bg)',
        color: 'var(--horosa-text)',
        stroke: 'var(--horosa-text)',
    };

    return (
        <Layout
            className={`${styles.horosaAppShell} horosa-workspace-shell`}
            data-appearance={resolvedAppearance}
            style={mainstyle}
        >
            <Header style={headerstyle}>
                <PageHeader 
                    admin={admin}
                    chartDisplay={chartDisplay}
                    appearanceMode={appearanceMode}
                    resolvedAppearance={resolvedAppearance}
                    userInfo={userInfo} 
                    onMenuClick={menuClick}
                    dispatch={dispatch}
                />
            </Header>

            <Content id='mainContent' style={contentStyle}>
                <div className={styles.workspaceOuter}>
                    <BackTop visibilityHeight={50}/>
                    <div className={styles.workspaceInner}>
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
