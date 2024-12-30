import basicAuth from 'basic-auth';

export default function auth(req, res, next) {
  const user = basicAuth(req);
  const username = process.env.BASIC_AUTH_USERNAME;
  const password = process.env.BASIC_AUTH_PASSWORD;

  if (!user || user.name !== username || user.pass !== password) {
    res.setHeader('WWW-Authenticate', 'Basic realm="example"');
    res.statusCode = 401;
    res.end('Access denied');
    return;
  }

  next();
} 