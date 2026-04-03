const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: "ap-southeast-2_P6Y2ebFof",
      userPoolClientId: "3oqvbm2ad04rethjh03lli30ml",
      loginWith: {
        email: true,
      },
    },
  },
};

export default awsConfig;
