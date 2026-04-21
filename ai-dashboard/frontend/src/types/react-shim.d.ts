declare module "react" {
  export function useEffect(effect: () => void | (() => void), deps?: unknown[]): void;
  export function useMemo<T>(factory: () => T, deps: unknown[]): T;
  export function useState<T>(initial: T | (() => T)): [T, (value: T | ((previous: T) => T)) => void];

  const React: {
    StrictMode: (props: { children?: unknown }) => JSX.Element;
  };
  export const StrictMode: (props: { children?: unknown }) => JSX.Element;
  export default React;
}

declare module "react-dom/client" {
  export function createRoot(container: Element | DocumentFragment): {
    render(children: JSX.Element): void;
  };
}

declare module "react/jsx-runtime" {
  export function jsx(type: unknown, props: unknown, key?: unknown): JSX.Element;
  export function jsxs(type: unknown, props: unknown, key?: unknown): JSX.Element;
  export const Fragment: unknown;
}

declare namespace JSX {
  interface Element {}

  interface IntrinsicElements {
    [elementName: string]: unknown;
  }
}
