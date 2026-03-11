import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AnalysisResponse, CounterpartyInput } from '../models/analysis.model';

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  generateAnalysis(
    counterparty: CounterpartyInput,
    analysisText: string
  ): Observable<AnalysisResponse> {
    const payload = {
      counterparty,
      analysis_input: {
        analysis_text: analysisText
      }
    };

    return this.http.post<AnalysisResponse>(`${this.apiUrl}/analyze`, payload);
  }

  getAnalysis(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/analysis/${id}`);
  }

  exportPDF(analysisId: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/export/pdf`,
      { analysis_id: analysisId },
      { responseType: 'blob' }
    );
  }

  exportDOCX(analysisId: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/export/docx`,
      { analysis_id: analysisId },
      { responseType: 'blob' }
    );
  }

  generateAnalysisWithFile(
    counterparty: CounterpartyInput,
    file: File
  ): Observable<AnalysisResponse> {
    return new Observable(observer => {
      const reader = new FileReader();
      
      reader.onload = () => {
        const base64 = reader.result as string;
        // Remove the data URL prefix (e.g., "data:application/pdf;base64,")
        const base64Data = base64.split(',')[1];
        
        // Determine file type
        const isPdf = file.type === 'application/pdf';
        const isDocx = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
        
        const payload = {
          counterparty,
          analysis_input: {
            analysis_text: null,
            pdf_file: isPdf ? base64Data : null,
            docx_file: isDocx ? base64Data : null
          }
        };

        this.http.post<AnalysisResponse>(`${this.apiUrl}/analyze`, payload)
          .subscribe({
            next: (response) => observer.next(response),
            error: (error) => observer.error(error),
            complete: () => observer.complete()
          });
      };
      
      reader.onerror = () => {
        observer.error(new Error('Failed to read file'));
      };
      
      reader.readAsDataURL(file);
    });
  }

  generateAnalysisWithUrl(
    counterparty: CounterpartyInput,
    url: string
  ): Observable<AnalysisResponse> {
    // For now, URL fetching would need backend support
    // This is a placeholder that could be implemented later
    throw new Error('URL input not yet supported by backend');
  }
}
