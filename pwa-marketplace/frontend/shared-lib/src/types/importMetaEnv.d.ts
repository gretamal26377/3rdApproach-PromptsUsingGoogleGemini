/// <reference types="vite/client" />

declare interface ImportMeta {
  env: {
    VITE_APP_TYPE?: string;
    [key: string]: any;
  };
}
