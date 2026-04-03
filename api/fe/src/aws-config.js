const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: "ap-southeast-2_BRF4PgaIU",
      userPoolClientId: "2s2os6v5hq4eecd969a2d5p2j8",
      loginWith: {
        email: true,
      },
    },
  },
};

export default awsConfig;
