import model
import helper as helper
import json
import httpx

def worldbank_parser(json_data, db:list):
    pids = list(json_data['projects'].keys())
    for pid in pids:
        jdata = json_data['projects'][pid]
        status = jdata.get('status')
        countries = jdata.get('countryname')
        title = jdata.get('project_name')
        date = jdata.get('boardapprovaldate')
        project_url = f'https://projects.worldbank.org/en/projects-operations/project-detail/{pid}'
        sectors = [tag['name'] for tag in jdata['theme_list']] if jdata.get('theme_list') else None
        sectors = '; '.join(sectors) if sectors else None
        project_data = {
            'status': status,
            'countries': countries,
            'sectors': sectors,
            'title': title,
            'project_url': project_url,
            'directory': 'World Bank',
            'date': date
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))

def start(db: list):
    url = "https://search.worldbank.org/api/v3/projects?format=json&rows=100&fct=projectfinancialtype_exact,status_exact,regionname_exact,themev2_level1_exact,themev2_level2_exact,themev2_level3_exact,sector_exact,countryshortname_exact,cons_serv_reqd_ind_exact,esrc_ovrl_risk_rate_exact&fl=id,regionname,countryname,projectstatusdisplay,project_name,countryshortname,pdo,impagency,cons_serv_reqd_ind,url,boardapprovaldate,closingdate,projectfinancialtype,curr_project_cost,ibrdcommamt,idacommamt,totalamt,grantamt,borrower,lendinginstr,envassesmentcategorycode,esrc_ovrl_risk_rate,sector1,sector2,sector3,theme1,theme2,%20%20status,totalcommamt,proj_last_upd_date,curr_total_commitment,curr_ibrd_commitment,curr_ida_commitment,last_stage_reached_name,theme_list,ida_cmt_usd_amt,cmt_usd_amt,projectcost&apilang=en&status_exact=Active^Pipeline&os=0"
    num = 0
    while True:
        print(f'Page: {num}')
        response = httpx.get(url, timeout=None)
        json_data = response.json()
        pids = list(json_data['projects'].keys())
        print(len(pids))
        if len(pids) > 0:
            worldbank_parser(json_data, db)
        else:
            break
        url = url.replace(f'os={num}', f'os={num+100}')
        num += 100
    
def main():
    db = helper.DB()
    start(db.projects)
    return db.projects