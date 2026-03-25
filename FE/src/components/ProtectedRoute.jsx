import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getCurrentUser, fetchAuthSession } from "aws-amplify/auth";

export default function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let mounted = true;

    async function checkAuth() {
      try {
        await getCurrentUser();
        const session = await fetchAuthSession();

        const hasToken = Boolean(
          session?.tokens?.idToken || session?.tokens?.accessToken,
        );

        if (!mounted) return;

        if (hasToken) {
          setStatus("authenticated");
        } else {
          setStatus("unauthenticated");
        }
      } catch (err) {
        if (!mounted) return;
        setStatus("unauthenticated");
      }
    }

    checkAuth();

    return () => {
      mounted = false;
    };
  }, []);

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-slate-600 text-sm">Checking authentication...</div>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: window.location.pathname }}
      />
    );
  }

  return children;
}
