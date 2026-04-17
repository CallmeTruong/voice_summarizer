const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: "ap-southeast-1_NDVKotIe6",
      userPoolClientId: "1l6d14a5hsg329p8nnuhegdlh4",
      loginWith: {
        email: true,
      },
    },
  },
};

export default awsConfig;
