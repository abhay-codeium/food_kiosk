export default () => {
  // Mock the window.location.href
  Object.defineProperty(window, 'location', {
    value: {
      href: 'http://localhost/'
    }
  });
};
