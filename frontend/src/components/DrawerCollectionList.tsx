import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import { makeStyles, Theme, createStyles } from '@material-ui/core/styles';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import VisibilitySensor from 'react-visibility-sensor';
import { StoreProps } from '../types/PropsTypes'
import { List } from '@material-ui/core';
import { Collection } from '../types/ModelTypes';
import { CollectionStore } from '../stores/CollectionStore';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    nested: {
      paddingLeft: theme.spacing(4),
      fontStyle: 'italic'
    },
  }),
);

interface DrawerCollectionListItemProps {
  store: CollectionStore
  collection: Collection
}

const DrawerCollectionListItem: React.FC<DrawerCollectionListItemProps> = ({ store, collection }) => {
  const classes = useStyles();

  function handleListItemClick(
    event: React.MouseEvent<HTMLLIElement, MouseEvent>,
    index: number,
  ): void {
    store.toggleDrawerSelectedCollection(index);
  }

  function isSelected(collectionId: number): boolean {
    return store.drawerSelectedCollection === collectionId
  }

  return (
    <React.Fragment>
      <ListItem
        selected={isSelected(collection.id)}
        onClick={event => handleListItemClick(event, collection.id)}
      >
        <ListItemText primary={collection.name} />
        {isSelected(collection.id) ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Collapse in={isSelected(collection.id)} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          <ListItem button className={classes.nested}>
            <Link to={`/keywords/${collection.id}`}><ListItemText primary="Overview" /></Link>
          </ListItem>
          {collection.keywords.map(keyword => (
            <ListItem button key={keyword.id} className={classes.nested}>
              <Link to={`/keywords/${collection.id}/${keyword.id}/`}>
                <ListItemText primary={keyword.name} />
              </Link>
            </ListItem>
          ))}
        </List>
      </Collapse>
    </React.Fragment>
  )
}

export const DrawerCollectionList: React.FC<StoreProps> = observer(({ store }) => {
  const loadMore = () => store.getCollections(store.collections.length)

  return (
    <List>
      {store.collections.map((collection, index) => {
        if (store.collectionHasMore && index === store.collections.length - 3) {
          return (
            <VisibilitySensor key={collection.id}>
              {({ isVisible }) => {
                if (isVisible) {
                  loadMore()
                }
                return (<DrawerCollectionListItem store={store} collection={collection} />)
              }}
            </VisibilitySensor>)
        } else {
          return (<DrawerCollectionListItem key={collection.id} store={store} collection={collection} />)
        }
      }
      )}
    </List>
  )
})
