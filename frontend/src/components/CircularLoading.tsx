/* eslint-disable no-script-url */

import React from 'react';
import { observer } from 'mobx-react';
import { CollectionStore } from '../stores/CollectionStore';
import CircularProgress from '@material-ui/core/CircularProgress';
import Fade from '@material-ui/core/Fade';

interface CircularLoadingProps {
  store: CollectionStore
}

export const CircularLoading: React.FC<CircularLoadingProps> = observer(({ store }) => {

  return (
    <React.Fragment>
      <Fade
        in={store.loading}
        style={{
          transitionDelay: store.loading ? '200ms' : '0ms',
        }}
        unmountOnExit
      >
        <div style={{display: 'flex', justifyContent: 'center'}}>
          <CircularProgress disableShrink />
        </div>
      </Fade>
    </React.Fragment>
  )
})

export default CircularLoading