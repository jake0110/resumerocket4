import React, { ReactNode } from 'react';

type LayoutProps = {
  children: ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-xl">My Next.js App</h1>
      </header>
      <main className="p-4">
        {children}
      </main>
      <footer className="bg-blue-600 text-white p-4 text-center">
        © 2023 My Next.js App
      </footer>
    </div>
  );
};

export default Layout; 