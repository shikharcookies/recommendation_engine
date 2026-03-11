import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private darkModeSubject = new BehaviorSubject<boolean>(true); // Default to dark mode
  darkMode$ = this.darkModeSubject.asObservable();

  constructor() {
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      this.darkModeSubject.next(savedTheme === 'dark');
    }
    this.applyTheme(this.darkModeSubject.value);
  }

  toggleTheme() {
    const newMode = !this.darkModeSubject.value;
    this.darkModeSubject.next(newMode);
    this.applyTheme(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  }

  private applyTheme(isDark: boolean) {
    if (isDark) {
      document.body.classList.add('dark-theme');
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
      document.body.classList.remove('dark-theme');
    }
  }

  isDarkMode(): boolean {
    return this.darkModeSubject.value;
  }
}
