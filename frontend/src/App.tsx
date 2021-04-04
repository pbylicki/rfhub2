import React from 'react';
import { Link, Route, RouteComponentProps, withRouter } from 'react-router-dom';
import clsx from 'clsx';
import queryString, { ParsedQuery } from 'query-string';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import { DrawerCollectionList } from './components/DrawerCollectionList';
import CollectionList from './components/CollectionList';
import { collectionStore } from './stores/CollectionStore';
import SearchKeywordList from './components/SearchKeywordList';
import CollectionDetails from './components/CollectionDetails';
import SearchBar from './components/SearchBar';
import SearchModal from './components/SearchModal';
import './App.css';
import Copyright from './components/Copyright';
import { StoreProps } from './types/PropsTypes';
import { observer } from 'mobx-react';

interface CollectionDetailsMatchParams {
  id: string
}
interface KeywordDetailsMatchParams {
  id: string
  keywordId: string
}

const drawerWidth = 300;

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
    backgroundColor: '#3f51b5'
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  appBarTitle: {
    flexGrow: 1,
    marginBottom: 0,
    color: 'white'
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  fixedHeight: {
    height: 240,
  }
}));

const AppTitle: React.FC<StoreProps> = observer(({ store }) => {
  const classes = useStyles();
  const title = store.versionInfo ? store.versionInfo.title : "rfhub2"
  return (
    <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
      <Link to="/">
        {title}
      </Link>
    </Typography>
  )
})

export const App: React.FC<RouteComponentProps<any>> = ({ history }) => {
  const store = collectionStore;
  const classes = useStyles();
  const [open, setOpen] = React.useState(true);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handleSearchRoute = (props: RouteComponentProps) => {
    const queryParams: ParsedQuery<string> = queryString.parse(props.location.search)
    if (queryParams["q"]) {
      store.clearSearchResults()
      store.searchKeywords(queryParams["q"] as string)
    } else {
      store.searchKeywords("")
    }
    return <SearchKeywordList {...props} store={store} />
  }

  const handleCollectionRoute = (props: RouteComponentProps<CollectionDetailsMatchParams>) => {
    const collectionId = parseInt(props.match.params.id)
    store.getCollection(collectionId)
    return <CollectionDetails store={store} />
  }

  const handleKeywordRoute = (props: RouteComponentProps<KeywordDetailsMatchParams>) => {
    const collectionId = parseInt(props.match.params.id)
    const keywordId = parseInt(props.match.params.keywordId)
    store.getCollectionWithKeywordSelected(collectionId, keywordId)
    return <CollectionDetails store={store} />
  }

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="absolute" className={clsx(classes.appBar, open && classes.appBarShift)}>
        <Toolbar className={classes.toolbar}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
          >
            <MenuIcon />
          </IconButton>
          <AppTitle store={store} />
          <SearchModal />
          <SearchBar store={store} history={history} />
        </Toolbar>
      </AppBar>
      <Drawer
        className={classes.drawer}
        variant="persistent"
        anchor="left"
        open={open}
        classes={{
          paper: classes.drawerPaper,
        }}
      >
        <div className={classes.toolbarIcon}>
          <Typography component="h1" variant="h6" gutterBottom className={classes.appBarTitle}>Collections</Typography>
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon className={classes.appBarTitle} />
          </IconButton>
        </div>
        <Divider />
        <DrawerCollectionList store={store} />
      </Drawer>
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container maxWidth="lg" className={classes.container}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                <Route path="/" exact render={(props) => <CollectionList {...props} store={store} />} />
                <Route path="/search/" render={handleSearchRoute} />
                <Route path="/keywords/:id/" exact render={handleCollectionRoute} />
                <Route path="/keywords/:id/:keywordId" exact render={handleKeywordRoute} />
              </Paper>
            </Grid>
          </Grid>
        </Container>
        <Copyright store={store} />
      </main>
    </div>
  );
}

export default withRouter(App);
