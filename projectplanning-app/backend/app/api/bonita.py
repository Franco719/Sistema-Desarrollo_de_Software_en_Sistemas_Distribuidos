import os, requests


class BonitaAPI:
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.api_token = None  # Se guarda en el login
    
    
    def login(self, user: str, password: str) -> dict | None:
        """Logs into Bonita API. Returns the cookies if it logged, or None if not"""
        url = f"{os.getenv('BONITA_URL')}/loginservice"
        user_and_psw = {
            "username": user, #os.getenv('BONITA_USER'),
            "password": password, #os.getenv('BONITA_PSW')
        }
        response = self.session.post(url, data=user_and_psw)

        if response.status_code == 204:
            self.authenticated = True
            self.api_token = self.session.cookies.get("X-Bonita-API-Token")
            return response.cookies
        else:
            return None

    def logout(self) -> bool:
        """Logs out of Bonita API. Returns True if it logout or False if not"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/logoutservice")
        return response.status_code == 200


    def do_request(self, method: str, uri: str, json: dict | None = None, params: dict | None = None):
        """
        General request handler for Bonita API with auth headers
        """
        if not self.authenticated:
            login_result = self.login()
            if not login_result:
                print("ERROR: No se pudo autenticar con Bonita")
                return None

        url = f"{os.getenv('BONITA_URL')}{uri}"
        headers = {
            "X-Bonita-API-Token": self.api_token,
            "Content-Type": "application/json"
        }

        print(f"DEBUG: {method} {url}")
        if json:
            print(f"DEBUG: Payload: {json}")
        if params:
            print(f"DEBUG: Params: {params}")

        try:
            response = self.session.request(method, url, headers=headers, json=json, params=params)
            
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code in (200, 201, 204):
                print("SUCCESS: La consulta fue exitosa")
                try:
                    if response.text:
                        result = response.json()
                        print(f"DEBUG: Response: {result}")
                        return result
                    else:
                        return None
                except Exception as e:
                    print(f"ERROR: No se pudo parsear JSON: {e}")
                    return None
            else:
                print(f"ERROR: La consulta falló - Status: {response.status_code}")
                print(f"ERROR: Response: {response.text}")
                return None
        except Exception as e:
            print(f"ERROR: Excepción en la request: {e}")
            return None
    
    def get_processes(self) -> list[dict]:
        """Gets all the processes designed"""
        response = self.do_request("GET", "/API/bpm/process?p=0&c=10")
        
        if response and isinstance(response, list):
            return response
        else:
            return []
    
    # No lo probe
    def get_cant_processes(self) -> int:
        """Gets the cant of processes designed"""
        response = self.do_request("GET", "/API/bpm/process")
        
        if response: 
            return response['Content-Range']
        else:
            return None
        
    
    def get_process_id(self, process_name):
        """Gets a process id by its name"""
        response = self.do_request("GET", f"/API/bpm/process?f=name={process_name}&p=0&c=1&o=version%20desc&f=activationState=ENABLED")
        
        if response:
            return response[0].get("id")
        return None
            
    
    def get_process_by_id(self, process_id: int) -> dict:
        """Gets a process by his id. Returns the process if it exists, None otherwise"""
        response = self.do_request("GET", f"/API/bpm/process/{process_id}")
        
        if response:
            return response
        else:
            None
         
    
    def initiate_project_by_id(self, process_id) -> int:
        """Instatiate a project-planning process, and returns the caseId in Bonita if was instatiate, None otherwise"""
        response = self.do_request("POST", f"/API/bpm/process/{process_id}/instantiation")

        if response:
            return response['caseId']
        else:
            return None     
    
        
    def set_variable_by_case(self, case_id: int, variable: str, value, type: str) -> bool:
        """Sets a variable of a case by the case id"""
        url = f"/API/bpm/caseVariable/{case_id}/{variable}"
        payload = {
            "value": value,
            "type": type
        }
        
        response = self.do_request("PUT", url, json=payload)
        
        if response:
            return True
        else:
            return False
        
    
    def search_activity_by_case_id(self, case_id: str):
        """Returns the next activity to do in the case sended"""
        response = self.do_request("GET", f"/API/bpm/task?f=caseId={case_id}") # Probar con mandar parametros para mas prolijidad (en todos no en este solo)
        
        if response:
            print(f"Actividad: {response[0].get("id")}")
            return response[0].get("id")
        else:
            print(f"No se encontraron tareas para el case_id: {case_id}")
            return None
    
    
    def assign_task(self, task_id: str, user_id: str):
        """Assigns the task to the user sended"""
        payload = {"assigned_id": user_id}
        response = self.do_request("PUT", f"/API/bpm/userTask/{task_id}", json=payload)
        return response is not None
    
    
    def execute_user_task(self, task_id: str, payload: dict | None = None) -> bool:
        """Execute the task and continue to the next task. WARNING: the task must be assigned to a user, 
        otherwise it will not execute and produces a error"""
        response = self.do_request("POST", f"/API/bpm/userTask/{task_id}/execution", json=payload)
        
        if response:
            return True
        else:
            return False


    def get_user_id_by_username(self, user_name: str) -> str:
        """Gets a user id by his username"""
        response = self.do_request("GET", f"/API/identity/user?f=userName={user_name}")
        
        if response:
            return response[0].get("id")
        else:
            return None
        
    
    def create_bonita_user(self, username: str, password: str, firstname: str, email: str, lastname: str, enabled: bool) -> str:
        """Creates a user and returns his id in bonita"""
        payload = {
            "userName": username,
            "password": password,
            "password_confirm": password,
            "firstname": firstname,
            "lastname": lastname,
            "enabled": str(enabled).lower(),
        }
        
        response = self.do_request("POST", "/API/identity/user", json=payload)
        if response:
            user_id = response.get("id")
            payload = {
                "id": user_id,
                "email": email,
            }
            response = self.do_request("PUT", f"/API/identity/personalcontactdata/{user_id}", json=payload)
            return user_id
        else:
            return None
    
    
    def delete_user_by_id(self, id: str):
        """Deletes a user by his id"""
        response = self.do_request("DELETE", f"/API/identity/user/{id}")
        
    
    def get_group_id(self, group_name: str) -> str:
        """Gets the group id by his name"""
        response = self.do_request("GET", f"/API/identity/group?f=name={group_name}")
        
        if response:
            return response[0].get("id")
        else:
            return None
        
    
    def get_role_id(self, role_name: str) -> str:
        """Gets the role id by his name"""
        response = self.do_request("GET", f"/API/identity/role?f=name={role_name}")
        
        if response:
            return response[0].get("id")
        else:
            return None
        
    
    def create_membership(self, user_id, role_id, group_id) -> bool:
        """Creates membership to a user, and returns de id of the user in the membership"""
        payload = {
            "role_id": role_id,
            "group_id": group_id,
            "user_id": user_id,
        }
        
        response = self.do_request("POST", "/API/identity/membership", json=payload)
        
        if response:
            return response.get("user_id")
        else:
            return None

    def get_active_cases(self):
        """Gets all active cases (open processes) from Bonita"""
        response = self.do_request("GET", "/API/bpm/case?p=0&c=100&d=processDefinitionId&d=started_by&d=startedBySubstitute")
        return response if response else []
    
    
    def get_pending_human_tasks(self):
        """Gets all pending human tasks with state=ready"""
        response = self.do_request("GET", "/API/bpm/humanTask?p=0&c=100&f=state=ready&d=processId&d=assigned_id&d=rootContainerId")
        return response if response else []

        
# Patron Singleton, en cada controlador llamo a esta función y me da una instancia de la api.
def get_bonita_api(user: str, password: str) -> BonitaAPI:
    """Returns a BonitaAPI instance"""
    if not hasattr(get_bonita_api, "_instance"):
        api = BonitaAPI()
        api.login(user, password)
        get_bonita_api._instance = api
    return get_bonita_api._instance

