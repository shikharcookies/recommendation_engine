import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

import { AnalysisService } from '../../services/analysis.service';
import { ThemeService } from '../../services/theme.service';
import { CounterpartyInput, AnalysisResponse } from '../../models/analysis.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatSnackBarModule,
    MatIconModule,
    MatButtonToggleModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  counterparty: CounterpartyInput = {
    name: '',
    country: '',
    sector: ''
  };

  // Input method selection
  inputMethod: 'text' | 'file' | 'url' = 'text';
  
  // Different input types
  analysisText = '';
  analysisUrl = '';
  selectedFile: File | null = null;
  selectedFileName = '';
  
  loading = false;
  analysisResult: AnalysisResponse | null = null;
  showBenchmarks = false;

  constructor(
    private analysisService: AnalysisService,
    private snackBar: MatSnackBar,
    public themeService: ThemeService
  ) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      // Check file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(file.type)) {
        this.snackBar.open('Please select a PDF or DOCX file', 'Close', { duration: 3000 });
        return;
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        this.snackBar.open('File size must be less than 10MB', 'Close', { duration: 3000 });
        return;
      }
      
      this.selectedFile = file;
      this.selectedFileName = file.name;
    }
  }

  clearFile() {
    this.selectedFile = null;
    this.selectedFileName = '';
  }

  generateRecommendation() {
    if (!this.counterparty.name) {
      this.snackBar.open('Please provide counterparty name', 'Close', {
        duration: 3000
      });
      return;
    }

    // Validate based on input method
    if (this.inputMethod === 'text' && !this.analysisText) {
      this.snackBar.open('Please provide analysis text', 'Close', { duration: 3000 });
      return;
    }
    
    if (this.inputMethod === 'file' && !this.selectedFile) {
      this.snackBar.open('Please select a file', 'Close', { duration: 3000 });
      return;
    }
    
    if (this.inputMethod === 'url' && !this.analysisUrl) {
      this.snackBar.open('Please provide a URL', 'Close', { duration: 3000 });
      return;
    }

    this.loading = true;
    
    if (this.inputMethod === 'text') {
      this.analysisService.generateAnalysis(this.counterparty, this.analysisText)
        .subscribe({
          next: (result) => {
            this.analysisResult = result;
            this.loading = false;
            this.snackBar.open('Analysis completed successfully!', 'Close', {
              duration: 3000
            });
          },
          error: (error) => {
            this.loading = false;
            this.snackBar.open(`Error: ${error.error?.detail || 'Failed to generate analysis'}`, 'Close', {
              duration: 5000
            });
          }
        });
    } else if (this.inputMethod === 'file' && this.selectedFile) {
      this.analysisService.generateAnalysisWithFile(this.counterparty, this.selectedFile)
        .subscribe({
          next: (result) => {
            this.analysisResult = result;
            this.loading = false;
            this.snackBar.open('Analysis completed successfully!', 'Close', {
              duration: 3000
            });
          },
          error: (error) => {
            this.loading = false;
            this.snackBar.open(`Error: ${error.error?.detail || 'Failed to generate analysis'}`, 'Close', {
              duration: 5000
            });
          }
        });
    } else if (this.inputMethod === 'url') {
      this.loading = false;
      this.snackBar.open('URL input not yet supported by backend', 'Close', { duration: 3000 });
    }
  }

  exportPDF() {
    if (!this.analysisResult) return;

    this.analysisService.exportPDF(this.analysisResult.analysis_id)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `recommendation_${this.analysisResult!.analysis_id}.pdf`;
          a.click();
          window.URL.revokeObjectURL(url);
        },
        error: (error) => {
          this.snackBar.open('Failed to export PDF', 'Close', { duration: 3000 });
        }
      });
  }

  exportDOCX() {
    if (!this.analysisResult) return;

    this.analysisService.exportDOCX(this.analysisResult.analysis_id)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `recommendation_${this.analysisResult!.analysis_id}.docx`;
          a.click();
          window.URL.revokeObjectURL(url);
        },
        error: (error) => {
          this.snackBar.open('Failed to export DOCX', 'Close', { duration: 3000 });
        }
      });
  }

  getOverallScore(): number {
    if (!this.analysisResult) return 0;
    const scores = this.analysisResult.scores;
    return (scores.asset_quality + scores.liquidity + scores.capitalisation + scores.profitability) / 4;
  }

  getBullets(key: string): string[] | null {
    if (!this.analysisResult?.structured_analysis_bullets) return null;
    const bullets = this.analysisResult.structured_analysis_bullets[key];
    return bullets && bullets.length > 0 ? bullets : null;
  }
}
