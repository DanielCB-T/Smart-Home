export type DeviceType = 'luz' | 'ventilador' | 'puerta' | 'alarma';
export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  on?: boolean;
  open?: boolean;
}
export interface HistoryEntry {
  id: number;
  timestamp: string;
  command: string;
  message: string;
  success: boolean;
  skipped: boolean;
}
export interface HomeState {
  devices: Device[];
  temperature: number;
  history: HistoryEntry[];
}
export interface CommandResponse extends HomeState {
  result: HistoryEntry;
}
