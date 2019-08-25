import React from 'react';
import { observer } from 'mobx-react';
import { makeStyles, Theme, createStyles } from '@material-ui/core/styles';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import { StoreProps } from '../types/PropsTypes'
import { List } from '@material-ui/core';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    nested: {
      paddingLeft: theme.spacing(4),
      fontStyle: 'italic'
    },
  }),
);

export const DrawerCollectionList: React.FC<StoreProps> = observer(({ store }) => {
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
  <List>
    {store.collections.map(collection => (
      <React.Fragment key={collection.id}>
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
          <ListItemText primary="Overview" />
        </ListItem>
        {collection.keywords.map(keyword => (
          <ListItem button key={keyword.id} className={classes.nested}>
          <ListItemText primary={keyword.name} />
        </ListItem>
        ))}
      </List>
      </Collapse>
      </React.Fragment>
    )
    )}
  </List>
  )
})
