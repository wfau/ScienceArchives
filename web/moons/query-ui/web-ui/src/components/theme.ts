const getStoredTheme = () => localStorage.getItem('theme')

export const getPreferredTheme = () => {
  const storedTheme = getStoredTheme()
  if (storedTheme) {
    return storedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const getCurrentTheme = () => {
  const storedTheme = getStoredTheme()
  if (storedTheme && storedTheme !== 'auto') {
    return storedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}
