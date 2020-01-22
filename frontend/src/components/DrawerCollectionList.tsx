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
import Tooltip from 'react-tooltip-lite'
import EllipsisText from "react-ellipsis-text";

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

const DrawerCollectionListItem: React.FC<DrawerCollectionListItemProps> = observer(({ store, collection }) => {
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
      {(collection.name.length > 32) ? (
        <Tooltip content={collection.name} direction="right" distance={26}>
          <ListItem
            selected={isSelected(collection.id)}
            onClick={event => handleListItemClick(event, collection.id)}
          >
            <ListItemText disableTypography>
              <EllipsisText
                text={collection.name}
                length='32'
              />
            </ListItemText>
            {isSelected(collection.id) ? <ExpandLess /> : <ExpandMore />}
          </ListItem>
        </Tooltip>
        ) : (
        <ListItem
          selected={isSelected(collection.id)}
          onClick={event => handleListItemClick(event, collection.id)}
        >
          <ListItemText disableTypography>
            <EllipsisText
              text={collection.name}
              length='32'
            />
          </ListItemText>
          {isSelected(collection.id) ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        )
      }
      <Collapse in={isSelected(collection.id)} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          <Link to={`/keywords/${collection.id}`}>
            <ListItem button className={classes.nested}>
              <ListItemText primary="Overview" disableTypography />
            </ListItem>
          </Link>
          {collection.keywords.map(keyword => {
            if (keyword.name.length > 32) {
              return (
                <Tooltip content={keyword.name} direction="right" distance={26}>
                  <Link to={`/keywords/${collection.id}/${keyword.id}/`}>
                    <ListItem button key={keyword.id} className={classes.nested}>
                      <ListItemText disableTypography>
                        <EllipsisText
                          text={keyword.name}
                          length='32'
                        />
                      </ListItemText>
                    </ListItem>
                  </Link>
                </Tooltip>
              )
            } else {
              return (
                <Link to={`/keywords/${collection.id}/${keyword.id}/`}>
                  <ListItem button key={keyword.id} className={classes.nested}>
                    <ListItemText primary={keyword.name} disableTypography />
                  </ListItem>
                </Link>
              )
            }
          })}
        </List>
      </Collapse>
    </React.Fragment>
  )
})

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
