import React from 'react';

import ResizeModeActions from 'components/ResizeModeActions/ResizeModeActions';

import { ResizeModeEnum } from 'config/enums/tableEnums';

import { IResizePanelProps } from 'types/components/ResizePanel/ResizePanel';

import './ResizePanel.scss';

function ResizePanel({
  panelResizing,
  resizeElemRef,
  resizeMode,
  onTableResizeModeChange,
  className,
}: IResizePanelProps): React.FunctionComponentElement<React.ReactNode> | null {
  return (
    <div
      ref={resizeElemRef}
      className={`${className || ''} ResizePanel${
        resizeMode === ResizeModeEnum.Hide && !panelResizing
          ? '__fullHeight'
          : resizeMode !== ResizeModeEnum.Resizable
          ? '__hidden'
          : ''
      } ${panelResizing ? 'resizing' : ''}`}
    >
      {resizeMode === ResizeModeEnum.Hide ? (
        <ResizeModeActions
          resizeMode={resizeMode}
          onTableResizeModeChange={onTableResizeModeChange}
        />
      ) : (
        <div className='ResizePanel__dots'>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}
    </div>
  );
}

export default React.memo(ResizePanel);
