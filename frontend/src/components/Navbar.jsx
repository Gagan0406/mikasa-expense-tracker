import React, { useState, useEffect, useRef } from 'react';
import { UserRound, Menu, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link, NavLink } from 'react-router-dom';

const Logo = () => (
  <svg width="150" height="40" viewBox="0 0 150 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="iconGradient" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#22D3EE"/>
        <stop offset="100%" stopColor="#34D399"/> 
      </linearGradient>
    </defs>
    <g id="icon">
      <rect x="0" y="12" width="9" height="21" rx="2.5" fill="url(#iconGradient)"/>
      <rect x="12" y="0" width="9" height="33" rx="2.5" fill="url(#iconGradient)"/>
      <rect x="24" y="9" width="9" height="24" rx="2.5" fill="url(#iconGradient)"/>
    </g>
    <text x="45" y="28" fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" fontSize="22" fontWeight="600" fill="#FFFFFF">
      Mikasa
    </text>
  </svg>
);

function Navbar() {
  const { user, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMenuOpen]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [menuRef]);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <header ref={menuRef}>
      {/* Backdrop Overlay */}
      <div 
        className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-10 transition-opacity duration-300 ${isMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={closeMenu}
        aria-hidden="true"
      ></div>

      <nav className="relative bg-gray-900 text-white shadow-md z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Logo - Always visible */}
            <div className="flex-shrink-0">
              <Link to="/dashboard">
                <Logo />
              </Link>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex md:items-center md:space-x-8">
              <NavLink to="/dashboard" className={({isActive}) => `px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'text-white bg-slate-800' : 'text-slate-300 hover:text-white'}`}>Dashboard</NavLink>
              <NavLink to="/transactions" className={({isActive}) => `px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'text-white bg-slate-800' : 'text-slate-300 hover:text-white'}`}>Transactions</NavLink>
              
              <div className="flex items-center space-x-4">
                 <div className="flex items-center space-x-2">
                   <UserRound size={20} className="text-slate-400" />
                   <span className="font-medium text-sm">{user?.name}</span>
                 </div>
                 <button
                   onClick={logout}
                   className="bg-red-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-red-700 transition-colors text-sm"
                 >
                   Logout
                 </button>
              </div>
            </div>

            {/* Mobile Menu Button - The only thing on the right side on mobile */}
            <div className="md:hidden flex items-center">
              <button onClick={() => setIsMenuOpen(!isMenuOpen)} aria-label="Open main menu" className="z-30">
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Panel */}
        <div className={`absolute top-full left-0 w-full bg-gray-900 md:hidden transition-transform duration-300 ease-in-out ${isMenuOpen ? 'transform translate-y-0' : 'transform -translate-y-[150%]'}`}>
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <NavLink to="/dashboard" onClick={closeMenu} className={({isActive}) => `block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-white bg-slate-800' : 'text-slate-300 hover:text-white'}`}>Dashboard</NavLink>
            <NavLink to="/transactions" onClick={closeMenu} className={({isActive}) => `block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-white bg-slate-800' : 'text-slate-300 hover:text-white'}`}>Transactions</NavLink>
            
            {/* Mobile User Profile & Sign Out Button */}
            <div className="border-t border-slate-700 mt-4 pt-4">
                <div className="flex items-center px-3">
                    <div className="flex-shrink-0">
                        <UserRound className="h-10 w-10 text-slate-400" />
                    </div>
                    <div className="ml-3">
                        <div className="text-base font-medium leading-none">{user?.name}</div>
                        <div className="text-sm font-medium leading-none text-slate-400">{user?.email}</div>
                    </div>
                </div>
                <div className="mt-3 px-2 space-y-1">
                    <button
                        onClick={() => { logout(); closeMenu(); }}
                        className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:text-white hover:bg-slate-800"
                    >
                        Sign out
                    </button>
                </div>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
