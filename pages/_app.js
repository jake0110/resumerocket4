import auth from '../middleware/auth';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

MyApp.getInitialProps = async ({ ctx }) => {
  auth(ctx.req, ctx.res, () => {});
  return {};
};

export default MyApp; 