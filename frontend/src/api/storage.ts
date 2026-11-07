const TOKEN_KEY = 'fmppi_access_token'
const REFRESH_KEY = 'fmppi_refresh_token'

export const storage = {
  getAccessToken: (): string | null => sessionStorage.getItem(TOKEN_KEY),
  setAccessToken: (value: string): void => sessionStorage.setItem(TOKEN_KEY, value),
  getRefreshToken: (): string | null => sessionStorage.getItem(REFRESH_KEY),
  setRefreshToken: (value: string): void => sessionStorage.setItem(REFRESH_KEY, value),
  clear: (): void => {
    sessionStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
  },
}

export default storage
