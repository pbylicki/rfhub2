/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import { StoreProps } from '../types/PropsTypes';

@observer
export default class CollectionDetails extends React.Component<StoreProps> {

  componentDidUpdate() {
    if (this.props.store.selectedKeywordId) {
      const element = document.getElementById(this.props.store.selectedKeywordId.toString());
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }

  render() {
    const store = this.props.store;
    let view
    if (store && store.detailCollection) {
      view = (
        <React.Fragment>
          <Title>{store.detailCollection.name}</Title>
          <div>version: {store.detailCollection.version}</div>
          <div>scope: {store.detailCollection.scope}</div>
          <div dangerouslySetInnerHTML={{ __html: store.detailCollection.html_doc }}></div>
          <Title>Keywords ({store.detailCollection.keywords.length})</Title>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Keyword</TableCell>
                <TableCell>Arguments</TableCell>
                <TableCell>Documentation</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {store.detailCollection.keywords.map(keyword => (
                <TableRow id={keyword.id.toString()} key={keyword.id}>
                  <TableCell>{keyword.name}</TableCell>
                  <TableCell>{keyword.arg_string}</TableCell>
                  <TableCell dangerouslySetInnerHTML={{ __html: keyword.html_doc }}></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </React.Fragment>
      )
    } else {
      view = (
        <React.Fragment>
          <Title>Collection not found</Title>
        </React.Fragment>
      )
    }

    return (
      <React.Fragment>
        {view}
      </React.Fragment>
    )
  }
}
