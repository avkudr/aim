import { IMediaPanelProps } from 'components/MediaPanel';
import { MediaTypeEnum } from 'components/MediaPanel/config';

import {
  IFocusedState,
  ITooltipContent,
} from 'types/services/models/metrics/metricsAppModel';

export interface IMediaSetProps {
  data: { [key: string]: any };
  orderedMap: { [key: string]: any };
  onListScroll: ({ scrollOffset: number }) => void;
  addUriToList: (blobUrl: string) => void;
  index?: number;
  mediaSetKey: number;
  wrapperOffsetHeight: number;
  wrapperOffsetWidth: number;
  // mediaItemHeight: number;
  syncHoverState?: (args: any) => void;
  focusedState: IFocusedState;
  additionalProperties?: IMediaPanelProps['additionalProperties'];
  tableHeight: IMediaPanelProps['tableHeight'];
  tooltip?: ITooltipContent;
  mediaType: MediaTypeEnum;
}
