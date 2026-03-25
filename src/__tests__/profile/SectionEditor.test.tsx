import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { patchSection } from '../../api/profile'
import SectionEditor from '../../components/profile/SectionEditor'

vi.mock('../../api/profile', () => ({
  patchSection: vi.fn().mockResolvedValue({}),
}))

const onSave = vi.fn()
const onCancel = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
})

describe('SectionEditor', () => {
  describe('summary', () => {
    it('renders a textarea with the current value', () => {
      render(<SectionEditor section="summary" data="Hello world" onSave={onSave} onCancel={onCancel} />)
      const textarea = screen.getByPlaceholderText('Write a brief summary about yourself...')
      expect(textarea).toBeInTheDocument()
      expect(textarea).toHaveValue('Hello world')
    })

    it('renders a label above the textarea', () => {
      render(<SectionEditor section="summary" data="" onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByText('Summary')).toBeInTheDocument()
    })

    it('calls patchSection and onSave when saved', async () => {
      render(<SectionEditor section="summary" data="Hello" onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      await waitFor(() => {
        expect(patchSection).toHaveBeenCalledWith('summary', 'Hello')
        expect(onSave).toHaveBeenCalled()
      })
    })
  })

  describe('skills', () => {
    it('renders text inputs for each skill', () => {
      render(<SectionEditor section="skills" data={['React', 'TypeScript']} onSave={onSave} onCancel={onCancel} />)
      const inputs = screen.getAllByPlaceholderText('Skill name')
      expect(inputs).toHaveLength(2)
      expect(inputs[0]).toHaveValue('React')
      expect(inputs[1]).toHaveValue('TypeScript')
    })

    it('can add a new skill', () => {
      render(<SectionEditor section="skills" data={['React']} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('+ Add Skill'))
      expect(screen.getAllByPlaceholderText('Skill name')).toHaveLength(2)
    })
  })

  describe('experience', () => {
    const exp = [{ company: 'Acme', role: 'Dev', start_date: '2020-01', end_date: '2022-06', accomplishments: ['Built stuff'] }]

    it('renders experience fields with labels', () => {
      render(<SectionEditor section="experience" data={exp} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByText('Company')).toBeInTheDocument()
      expect(screen.getByText('Title / Role')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Acme')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Dev')).toBeInTheDocument()
      expect(screen.getByDisplayValue('2020-01')).toBeInTheDocument()
      expect(screen.getByDisplayValue('2022-06')).toBeInTheDocument()
    })

    it('has a "Currently working here" checkbox that nulls end_date', () => {
      render(<SectionEditor section="experience" data={exp} onSave={onSave} onCancel={onCancel} />)
      const checkbox = screen.getByLabelText('Currently working here')
      expect(checkbox).not.toBeChecked()
      fireEvent.click(checkbox)
      expect(checkbox).toBeChecked()
      expect(screen.getByText('Present')).toBeInTheDocument()
    })

    it('validates date format on save', async () => {
      const badExp = [{ company: 'Acme', role: 'Dev', start_date: 'bad', end_date: '2022-06', accomplishments: [] }]
      render(<SectionEditor section="experience" data={badExp} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      expect(await screen.findByText('Use YYYY-MM')).toBeInTheDocument()
      expect(patchSection).not.toHaveBeenCalled()
    })

    it('validates required fields on save', async () => {
      const emptyExp = [{ company: '', role: '', start_date: '', end_date: '', accomplishments: [] }]
      render(<SectionEditor section="experience" data={emptyExp} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      const requiredErrors = await screen.findAllByText('Required')
      expect(requiredErrors.length).toBeGreaterThanOrEqual(2)
      expect(patchSection).not.toHaveBeenCalled()
    })

    it('has an x button to remove entries', () => {
      render(<SectionEditor section="experience" data={exp} onSave={onSave} onCancel={onCancel} />)
      const removeButtons = screen.getAllByText('x')
      // One for the entry, one for the accomplishment
      expect(removeButtons.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('activities', () => {
    const act = [{ name: 'haid-hunter', category: 'Project', url: 'https://github.com/example', details: ['Built with React'] }]

    it('renders activity fields with labels', () => {
      render(<SectionEditor section="activities" data={act} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByText('Name')).toBeInTheDocument()
      expect(screen.getByText('Category')).toBeInTheDocument()
      expect(screen.getByDisplayValue('haid-hunter')).toBeInTheDocument()
      expect(screen.getByDisplayValue('https://github.com/example')).toBeInTheDocument()
    })

    it('has a category dropdown', () => {
      render(<SectionEditor section="activities" data={act} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByDisplayValue('Project')).toBeInTheDocument()
    })

    it('validates required name on save', async () => {
      const empty = [{ name: '', category: '', details: [] }]
      render(<SectionEditor section="activities" data={empty} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      expect(await screen.findByText('Required')).toBeInTheDocument()
      expect(patchSection).not.toHaveBeenCalled()
    })

    it('renders details sub-section', () => {
      render(<SectionEditor section="activities" data={act} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByDisplayValue('Built with React')).toBeInTheDocument()
      expect(screen.getByText('+ Detail')).toBeInTheDocument()
    })
  })

  describe('education', () => {
    const edu = [{ institution: 'MIT', degree: 'BS', field: 'CS', start_date: '2016-09', end_date: '2020-05', details: ['Dean\'s List'] }]

    it('renders education fields with labels including field of study', () => {
      render(<SectionEditor section="education" data={edu} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByText('Institution')).toBeInTheDocument()
      expect(screen.getByText('Degree')).toBeInTheDocument()
      expect(screen.getByText('Field of Study')).toBeInTheDocument()
      expect(screen.getByDisplayValue('MIT')).toBeInTheDocument()
      expect(screen.getByDisplayValue('BS')).toBeInTheDocument()
      expect(screen.getByDisplayValue('CS')).toBeInTheDocument()
    })

    it('has a "Currently enrolled" checkbox', () => {
      render(<SectionEditor section="education" data={edu} onSave={onSave} onCancel={onCancel} />)
      const checkbox = screen.getByLabelText('Currently enrolled')
      expect(checkbox).not.toBeChecked()
      fireEvent.click(checkbox)
      expect(checkbox).toBeChecked()
    })

    it('renders details sub-section', () => {
      render(<SectionEditor section="education" data={edu} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByDisplayValue("Dean's List")).toBeInTheDocument()
      expect(screen.getByText('+ Detail')).toBeInTheDocument()
    })

    it('validates required fields on save', async () => {
      const emptyEdu = [{ institution: '', degree: '', field: '', start_date: '', end_date: '', details: [] }]
      render(<SectionEditor section="education" data={emptyEdu} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      const requiredErrors = await screen.findAllByText('Required')
      expect(requiredErrors.length).toBeGreaterThanOrEqual(2)
      expect(patchSection).not.toHaveBeenCalled()
    })
  })

  describe('certifications', () => {
    it('renders certification fields with labels', () => {
      const certs = [{ name: 'AWS SAA', issuer: 'Amazon', date: '2023-01' }]
      render(<SectionEditor section="certifications" data={certs} onSave={onSave} onCancel={onCancel} />)
      expect(screen.getByText('Certification Name')).toBeInTheDocument()
      expect(screen.getByText('Issuer')).toBeInTheDocument()
      expect(screen.getByDisplayValue('AWS SAA')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Amazon')).toBeInTheDocument()
      expect(screen.getByDisplayValue('2023-01')).toBeInTheDocument()
    })

    it('validates date format on save', async () => {
      const badCerts = [{ name: 'AWS', issuer: 'Amazon', date: 'nope' }]
      render(<SectionEditor section="certifications" data={badCerts} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      expect(await screen.findByText('Use YYYY-MM')).toBeInTheDocument()
      expect(patchSection).not.toHaveBeenCalled()
    })
  })

  describe('objectives', () => {
    it('renders a list of sentence inputs', () => {
      render(<SectionEditor section="objectives" data={['Get promoted', 'Learn Rust']} onSave={onSave} onCancel={onCancel} />)
      const inputs = screen.getAllByPlaceholderText('Objective statement')
      expect(inputs).toHaveLength(2)
      expect(inputs[0]).toHaveValue('Get promoted')
      expect(inputs[1]).toHaveValue('Learn Rust')
    })

    it('can add a new objective', () => {
      render(<SectionEditor section="objectives" data={['Get promoted']} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('+ Add Objective'))
      expect(screen.getAllByPlaceholderText('Objective statement')).toHaveLength(2)
    })
  })

  describe('sorting on save', () => {
    it('sorts experience most recent first', async () => {
      const items = [
        { company: 'Old', role: 'Dev', start_date: '2015-01', end_date: '2017-06', accomplishments: [] },
        { company: 'Current', role: 'Lead', start_date: '2022-01', end_date: null, accomplishments: [] },
        { company: 'Mid', role: 'Senior', start_date: '2018-01', end_date: '2021-12', accomplishments: [] },
      ]
      render(<SectionEditor section="experience" data={items} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      await waitFor(() => {
        const sorted = (patchSection as ReturnType<typeof vi.fn>).mock.calls[0][1]
        expect(sorted[0].company).toBe('Current')
        expect(sorted[1].company).toBe('Mid')
        expect(sorted[2].company).toBe('Old')
      })
    })

    it('sorts certifications most recent first', async () => {
      const items = [
        { name: 'Old', issuer: 'A', date: '2020-01' },
        { name: 'New', issuer: 'B', date: '2023-06' },
      ]
      render(<SectionEditor section="certifications" data={items} onSave={onSave} onCancel={onCancel} />)
      fireEvent.click(screen.getByText('Save'))
      await waitFor(() => {
        const sorted = (patchSection as ReturnType<typeof vi.fn>).mock.calls[0][1]
        expect(sorted[0].name).toBe('New')
        expect(sorted[1].name).toBe('Old')
      })
    })
  })

  it('calls onCancel when Cancel is clicked', () => {
    render(<SectionEditor section="summary" data="" onSave={onSave} onCancel={onCancel} />)
    fireEvent.click(screen.getByText('Cancel'))
    expect(onCancel).toHaveBeenCalled()
  })

  it('returns null for unknown section', () => {
    const { container } = render(<SectionEditor section="unknown" data={null} onSave={onSave} onCancel={onCancel} />)
    expect(container.innerHTML).toBe('')
  })
})
