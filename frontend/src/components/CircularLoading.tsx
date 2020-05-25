/* eslint-disable no-script-url */
import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import Fade from '@material-ui/core/Fade';

export const CircularLoading = ({ view }) => {

  return (
    <React.Fragment>
      <Fade
        in={ view }
        style={{
          transitionDelay: view ? '200ms' : '0ms',
        }}
        unmountOnExit
      >
        <div style={{display: 'flex', justifyContent: 'center', padding: '10px'}}>
          <CircularProgress disableShrink />
        </div>
      </Fade>
    </React.Fragment>
  )
}

export default CircularLoading