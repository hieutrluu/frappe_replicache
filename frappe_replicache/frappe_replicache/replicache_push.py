import frappe
from restipie.custom_api_core import request
from restipie.custom_api_core import response

@request("POST", "/v1/api/replicache_push")
def handlePush(req, res):
    pass

def processMutation(psg, clientID, mutation, spaceID, error):
    '''Process a mutation from the client'''
    _dict = frappe.db.sql(f"""select version from space where key = '{spaceID}' for update""").as_dict()
    nextVersion = _dict['prev_version'] + 1
    lastMutationID = getLatestMutationID(psg, clientID=clientID, required=False)
    nextMutationID = lastMutationID + 1

    if mutation.id < nextMutationID:
        raise Exception(f"Mutation ID has already been processed - skipping")

    if mutation.id > nextMutationID:
        raise Exception(f"Mutation ID is from the future - aborting")

    if (error == None):
        print(f'Processing mutation: {mutation}')
        if mutation.name == 'createMessage':
            createMessage(mutation.type, mutation.args, spaceID, nextVersion)
        else:
            raise Exception(f"Unknown mutation {mutation.name}")
    else:
        print(f'Error processing mutation: {mutation}')

    setLatestMutationID(psg, clientID, nextMutationID)
    # update version for space

    # WTF is t.none in pg-promise ???
#     await t.none('update space set version = $1 where key = $2', [
#     nextVersion,
#     spaceID,
#   ]);
    # frappe.db.set_value("Space", spaceID, "version", nextVersion)


def getLatestMutationID(psg, clientID, required):
    clientRow = frappe.db.get_value("Replicache Client", client_id=clientID, latest_mutation_id=required)
    if not clientRow:
        if required:
            raise Exception(f"Client not found {clientID}")
        return 0
    else:
        # TODO parse in correct format
        return clientRow.latest_mutation_id


def setLatestMutationID(psg, clientID, mutationID):
    '''using query builder to update client mutation'''
    # TODO: direct copy of the javascript which is incorrect, this need to check if there is any row with the clientID, mutationID and update them
    result = frappe.db.set_value("Replicache Client", client_id=clientID, latest_mutation_id=mutationID)

    if len(result) == 0:
        frappe.db.insert({
            "doctype": "Replicache Client",
            "client_id": clientID,
            "latest_mutation_id": mutationID
        })


def createMessage(t, {id, from, content, order}, spaceID, version):
    # using frappe query builder to insert into the database
    frappe.db.insert({
        "doctype": "Replicache Message",
        "type": t,
        "id": id,
        "from": from,
        "content": content,
        "order": order,
        "space_id": spaceID,
        "version": version
    })

def sendPoke(sio):
    '''Send a poke to the client to trigger a pull'''
    sio.emit('poke', channel='replicache')