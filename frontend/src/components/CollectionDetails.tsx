/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import { StoreProps } from '../types/PropsTypes'

export const CollectionDetails: React.FC<StoreProps> = observer(({ store }) => {
let view
if (store.detailCollection) {
  view = (
    <React.Fragment>
        <Title>{store.detailCollection.name}</Title>
        <div dangerouslySetInnerHTML={{__html: store.detailCollection.html_doc}}></div>
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
              <TableRow key={keyword.id}>
                <TableCell>{keyword.name}</TableCell>
                <TableCell>{keyword.arg_string}</TableCell>
                <TableCell dangerouslySetInnerHTML={{__html: keyword.html_doc}}></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </React.Fragment>
  )
}

  return (
    <React.Fragment>
      {view}
    </React.Fragment>
    )
});  
export default CollectionDetails