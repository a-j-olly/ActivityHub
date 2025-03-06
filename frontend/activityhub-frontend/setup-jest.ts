// setup-jest.ts
import { setupZoneTestEnv } from 'jest-preset-angular/setup-env/zone';

setupZoneTestEnv();

// Extend TypeScript types for jest
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveBeenCalledWith(...args: any[]): R;
      toBeTrue(): R;
      toBeFalse(): R;
      toBeTruthy(): R;
      toBeFalsy(): R;
    }
  }
}

// Global mocks for Window objects
Object.defineProperty(window, 'CSS', { value: null });

Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    display: 'none',
    appearance: ['-webkit-appearance'],
    getPropertyValue: () => ''
  })
});

Object.defineProperty(document, 'doctype', {
  value: '<!DOCTYPE html>'
});

Object.defineProperty(document.body.style, 'transform', {
  value: () => ({
    enumerable: true,
    configurable: true
  })
});

// AWS Amplify polyfills
Object.defineProperty(window, 'global', { value: window });
Object.defineProperty(window, 'process', {
  value: {
    env: { DEBUG: undefined },
    browser: true,
    version: ""
  }
});