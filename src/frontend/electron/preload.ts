import { ipcRenderer, contextBridge } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  getVersion: () => ipcRenderer.invoke('get-app-version'),
  minimize: () => ipcRenderer.invoke('minimize-window'),
  maximize: () => ipcRenderer.invoke('maximize-window'),
  close: () => ipcRenderer.invoke('close-window'),
})

export type ElectronAPI = typeof window.electronAPI
