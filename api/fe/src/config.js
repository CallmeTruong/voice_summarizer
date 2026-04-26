function getRequiredEnv(name) {
  const value = import.meta.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

function withoutTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}

export const API_BASE_URL = withoutTrailingSlash(
  getRequiredEnv("VITE_API_BASE_URL"),
);

export const COGNITO_USER_POOL_ID = getRequiredEnv(
  "VITE_COGNITO_USER_POOL_ID",
);

export const COGNITO_USER_POOL_CLIENT_ID = getRequiredEnv(
  "VITE_COGNITO_USER_POOL_CLIENT_ID",
);
